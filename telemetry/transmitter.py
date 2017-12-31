import logging
from abc import ABC, abstractmethod
from collections import OrderedDict
from threading import RLock, Thread, Condition

log = logging.getLogger(__name__)


class Transmitter(ABC):
    """
    The Transmitter is responsible to transmit measurements back to the
    monitoring station.
    """

    @abstractmethod
    def publish(self, measurements):
        """
        Transmits a single measurement or a `iterable` of measurement.

        :param measurement: A measurement or a iterable of measurements
        """


class DiscardTransmitter(Transmitter):
    def publish(self, measurements):
        pass


class BufferedTransmitter(Transmitter):
    """
    BufferedTransmitter is a decorator that buffer measurements and handles
    the actual transmission in background.

    It transmits(flushes) the data periodically or whenever the buffer reaches
    its `soft-limit`.

    *Understanding Buffer Limits*:

    The buffer has two limit definition:
      * Hard Limit: defined by the 'max_buffer_size' parameter - specifies
      the maximum number of measurements to be buffered;
      * Soft Limit: defined by 'max_buffer_size - 10%' - when it reaches its
      soft limit, this transmitter will try to flush its content in background.

    It's important to notice that although it tries the best to keep the buffer
    from reaching its hard limit, data loss may occurs - it'll discard old
    measurements to avoid buffer overflow.

    The BufferedTrasmitter never does flush operation in background, except if
    flush is explicitly called from outside.

    Finally, it guarantees that at any given moment
    buffer_capacity <= buffer_max_size
    """

    def __init__(self, transmitter, max_buffer_size=1000,
                 max_flush_interval_seconds=10):
        if max_buffer_size <= 0:
            raise ValueError('max_buffer_size must be greater than 0')
        if max_flush_interval_seconds <= 0:
            raise ValueError(
                'max_flush_interval_seconds must be greater than 0'
            )

        self._transmitter = transmitter
        self._limit = max_buffer_size
        self._max_interval = max_flush_interval_seconds

        self._buffer = OrderedDict()
        self._buffer_lock = RLock()
        self._flush_lock = Condition(RLock())

        self._flusher = Thread(
            name='BufferedTransmitterPeriodicallyFlusher',
            daemon=True,
            target=self._background_flush
        )
        self._flusher.start()

    @property
    def limit(self):
        return self._limit

    @property
    def remaining_capacity(self):
        with self._buffer_lock:
            return self.limit - len(self._buffer)

    @property
    def has_reached_soft_limit(self):
        remaining_percentage = self.remaining_capacity / self.limit * 100
        return remaining_percentage <= 10

    def publish(self, measurements, flush_full=True):
        with self._buffer_lock:
            self._buffer[measurements] = BufferedTransmitter
            self._ensure_buffer_has_capacity(flush_full)

    def flush(self):
        to_publish = self._to_publish()
        try:
            self._transmitter.publish(to_publish)
            log.debug('%s metrics published', len(to_publish))
        except Exception:
            log.warning('Failed to publish metrics', exc_info=1)
            self._rollback(to_publish)

    def _ensure_buffer_has_capacity(self, flush_full):
        if not self.remaining_capacity > 0:
            self._buffer.popitem(last=False)  # FIFO policy

        if flush_full and self.has_reached_soft_limit:
            with self._flush_lock:
                log.debug('Buffer is full flushing it. [Current size: %s]',
                          len(self._buffer))
                self._flush_lock.notify()

    def _to_publish(self):
        with self._buffer_lock:
            to_publish = self._buffer
            self._buffer = OrderedDict()
            return to_publish

    def _rollback(self, to_publish):
        # restore original metrics
        with self._buffer_lock:
            new_entries = self._buffer
            self._buffer = to_publish
            for entry in new_entries:
                self.publish(entry, flush_full=False)

    def _background_flush(self):
        log.debug('Buffer flusher Thread started.')
        with self._flush_lock:
            while True:
                # wait method releases the lock while sleeping and
                # re-acquire before continue
                self._flush_lock.wait(self._max_interval)
                self.flush()
