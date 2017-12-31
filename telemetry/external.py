from datetime import datetime

from telemetry.metrics import Measurement
from telemetry.transmitter import Transmitter

ISO_FORMAT = '%Y-%m-%dT%H:%M%S.%sZ'


def format_epoch(epoch_secs):
    dt = datetime.utcfromtimestamp(epoch_secs)
    return dt.strftime(ISO_FORMAT)


class InfluxTransmitter(Transmitter):
    def __init__(self, host='localhost', port=8086, user='', pwd='',
                 db='metrics'):
        self.host = host
        self.port = port
        self.user = user
        self.pwd = pwd
        self.db = db
        self._client = None

    @property
    def client(self):
        if not self._client:
            from influxdb import InfluxDBClient
            self._client = InfluxDBClient(
                self.host, self.port, self.user, self.pwd, self.db
            )
        return self._client

    def _transform(self, measurements):
        return [
            {
                'measurement': m.name,
                'tags': m.tags,
                'fields': {
                    'value': m.value
                },
                'time': format_epoch(m.timestamp)
            }
            for m in measurements
        ]

    def publish(self, measurements):
        if isinstance(measurements, Measurement):
            measurements = [measurements]

        self.client.write_points(self._transform(measurements))
