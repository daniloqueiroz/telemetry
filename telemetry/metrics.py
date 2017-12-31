import time
from abc import ABC
from contextlib import contextmanager


class Measurement:
    """
    A Measurement represents a single observed value at a given instant for
    a given property.

    Measurements are considered equals if they have the same name, value and
    timestamp.

    Measurements are immutable.
    """
    def __init__(self, metric_name, value, tags):
        self._name = metric_name
        self._value = value
        self._tags = tags
        self._timestamp = time.time()

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    @property
    def tags(self):
        return self._tags

    @property
    def timestamp(self):
        return self._timestamp

    def __eq__(self, other):
        if isinstance(other, Measurement):
            return (
                self.name == other.name and
                self.value == other.value and
                self.timestamp == other.timestamp
            )
        else:
            return False

    def __hash__(self):
        return hash((self.name, self.value, self.timestamp))


class Metric(ABC):
    """
    A Metric is a collection of measurements over time for the same property.
    Two measurements are considered as belonging to the same metric if both
    have the same name.

    Metric classes provide mechanisms to record multiple measurements for a
    single metric.
    """
    def __init__(self, name, recorder_fn):
        self._name = name
        self._recorder = recorder_fn

    @property
    def name(self):
        return self._name

    def record(self, value, tags):
        self._recorder(self.name, value, tags)


class Counter(Metric):
    """
    A simple increment or decrement metric. Useful for counting things.
    """
    def inc(self, tags=None):
        self.record(1, tags)

    def dec(self, tags=None):
        self.record(-1, tags)


class Gauge(Metric):
    """
    An arbitrary value metric.
    """
    def value(self, value, tags=None):
        self.record(value, tags)


class Timer(Metric):
    """
    A elapsed time metric.

    Timers provide you a context manager to be used for tracking time.
    """
    @contextmanager
    def timeit(self, tags=None):
        start = time.time()
        yield
        elapsed = time.time() - start
        self.record(elapsed, tags)
