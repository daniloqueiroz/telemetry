from telemetry.metrics import Measurement, Counter, Gauge, Timer
from telemetry.transmitter import Transmitter


class Telemeter(Transmitter):
    """
    Telemeter is the central piece for Telemetry of your application.

    Telemeter give you mechanism to record an arbitrary Measurement
    or use create Metrics to record different measurements to it.
    """
    def __init__(self, transmitter, default_tags=None):
        self._transmitter = transmitter
        self._default_tags = default_tags

    def _build_tags(self, tags=None):
        final_tags = {}
        if self._default_tags:
            final_tags.update(self._default_tags)
        if tags:
            final_tags.update(tags)
        return final_tags

    def publish(self, measurement):
        self._transmitter.publish(measurement)

    def record(self, metric_name, value, tags=None):
        m = Measurement(
            metric_name=metric_name,
            value=value,
            tags=self._build_tags(tags)
        )
        self.publish(m)

    def counter(self, name):
        return Counter(name, self.record)

    def gauge(self, name):
        return Gauge(name, self.record)

    def timer(self, name):
        return Timer(name, self.record)
