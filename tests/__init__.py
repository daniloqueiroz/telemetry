import time

from telemetry.metrics import Measurement
from telemetry.transmitter import Transmitter


class SimpleTransmitter(Transmitter):
    def __init__(self):
        self.measurements = []

    def publish(self, measurement):
        if isinstance(measurement, Measurement):
            self.measurements.append(measurement)
        else:
            for m in measurement:
                self.measurements.append(m)


class FaultyTransmitter(Transmitter):
    def publish(self, measurement):
        raise Exception()