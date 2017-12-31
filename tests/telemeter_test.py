from datetime import datetime, timedelta
from unittest import TestCase

from freezegun import freeze_time
from nose.tools import istest, eq_

from telemetry import Telemeter
from tests import SimpleTransmitter


class TelemeterMetricsTest(TestCase):
    def setUp(self):
        self.transmitter = SimpleTransmitter()
        self.telemeter = Telemeter(self.transmitter, {'app': 'unittest'})

    @istest
    def count_inc_metric(self):
        c = self.telemeter.counter('tests.counter')
        c.inc({'app': 'tests'})

        eq_(len(self.transmitter.measurements), 1)
        m = self.transmitter.measurements.pop()
        eq_(m.name, 'tests.counter')
        eq_(m.value, 1)
        eq_(m.tags, {'app': 'tests'})

    @istest
    def count_dec_metric(self):
        c = self.telemeter.counter('tests.counter')
        c.dec({'app': 'tests'})

        eq_(len(self.transmitter.measurements), 1)
        m = self.transmitter.measurements.pop()
        eq_(m.name, 'tests.counter')
        eq_(m.value, -1)
        eq_(m.tags, {'app': 'tests'})

    @istest
    def count_multiple_metric(self):
        c = self.telemeter.counter('tests.counter')
        c.inc()
        c.dec()
        c.inc()

        for i in (1, -1, 1):
            m = self.transmitter.measurements.pop()
            eq_(m.value, i)

    @istest
    def gauge_metric(self):
        g = self.telemeter.gauge('tests.gauge')
        g.value(42, {'app': 'tests'})
        eq_(len(self.transmitter.measurements), 1)
        m = self.transmitter.measurements.pop()
        eq_(m.name, 'tests.gauge')
        eq_(m.value, 42)
        eq_(m.tags, {'app': 'tests'})

    @istest
    def timer_metric(self):
        initial_datetime = datetime.utcnow()
        with freeze_time(initial_datetime) as now:

            t = self.telemeter.timer('tests.timer')
            with t.timeit({'app': 'tests'}):
                end_time = initial_datetime + timedelta(seconds=60)
                now.move_to(end_time)

        eq_(len(self.transmitter.measurements), 1)
        m = self.transmitter.measurements.pop()
        eq_(m.name, 'tests.timer')
        eq_(m.value, 60)
        eq_(m.tags, {'app': 'tests'})

    @istest
    def raw_measurement(self):
        self.telemeter.record('tests.raw', 728.2, {'source': 'raw'})

        eq_(len(self.transmitter.measurements), 1)
        m = self.transmitter.measurements.pop()
        eq_(m.name, 'tests.raw')
        eq_(m.value, 728.2)
        eq_(m.tags, {'app': 'unittest', 'source': 'raw'})