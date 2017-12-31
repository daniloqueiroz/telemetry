from unittest import TestCase

import time
from nose.tools import istest, eq_

from telemetry.metrics import Measurement
from telemetry.transmitter import BufferedTransmitter
from tests import SimpleTransmitter, FaultyTransmitter


class TelemeterMetricsTest(TestCase):
    def setUp(self):
        self.transmitter = SimpleTransmitter()
        self.buffered= BufferedTransmitter(
            self.transmitter,
            max_buffer_size=10,
            max_flush_interval_seconds=5
        )

    @istest
    def flushes_buffer_soft_limit_reached(self):
        for i in range(0, 9):
            self.buffered.publish(Measurement('tests.buffer', i, {}))

        # sleep just enough to give background thread a change to run
        time.sleep(0.01)

        eq_(len(self.transmitter.measurements), 9)

    @istest
    def flushes_periodically(self):
        self.buffered= BufferedTransmitter(
            self.transmitter,
            max_buffer_size=10,
            max_flush_interval_seconds=0.001
        )

        self.buffered.publish(Measurement('tests.buffer', 40, {}))
        self.buffered.publish(Measurement('tests.buffer', 42, {}))

        time.sleep(0.01)

        eq_(self.buffered.remaining_capacity, 10)
        eq_(len(self.transmitter.measurements), 2)

    @istest
    def flushes_fail_keep_buffer(self):
        self.transmitter = FaultyTransmitter()
        self.buffered= BufferedTransmitter(
            self.transmitter,
            max_buffer_size=10,
            max_flush_interval_seconds=5
        )

        self.buffered.publish(Measurement('tests.buffer', 40, {}))
        self.buffered.publish(Measurement('tests.buffer', 42, {}))

        capacity = self.buffered.remaining_capacity

        self.buffered.flush()

        eq_(self.buffered.remaining_capacity, capacity)
