# Telemetry

Telemetry is a python library to instrument your code and send
metrics to a monitoring station.

## Quick Start

```python
from telemetry import Telemeter
from telemetry.transmitter import DiscardTransmitter

telemeter = Telemeter(DiscardTransmitter)

requests = telemeter.counter('mysystem.requests')

requests.inc()

gauge = telemeter.gauge('mysystem.cache_size')
gauge.value(len(cache))

timer = telemeter.timer('mysystem.process_time')

with timer.timeit():
    time.sleep(5)

telemeter.record('mysystem.custom_metric', 0.42)
```

### Publishing to InfluxDB

To use InfluxTransmitter you need add `influxdb==5.0.0` to your requirements

```python
from telemetry import Telemeter
from telemetry.external import InfluxTransmitter

transmitter = InfluxTransmitter(
    host='influxdb',
    port=8086,
    user='root',
    pwd='secret',
    db='app_metrics'
)

telemeter = Telemeter(transmitter, {'app_name': 'my_app'})

# ...
```

This will send all the metrics to influx. However this will
make the transmission synchronous, what can affect your application
performance, so probably isn't what you want.

The next session show how to do it asynchronously!

### BufferedTransmitter

The BufferedTransmitter allows you to buffer your metrics and
send them periodically in background using any transmitter.

```python
from telemetry import Telemeter
from telemetry.external import InfluxTransmitter
from telemetry.transmitter import BufferedTransmitter

transmitter = InfluxTransmitter(
    host='influxdb',
    port=8086,
    user='root',
    pwd='secret',
    db='app_metrics'
)

buffered = BufferedTransmitter(
    transmitter,
    max_buffer_size=100,
    max_flush_interval_seconds=5
)

telemeter = Telemeter(buffered, {'app_name': 'my_app'})
```

The BufferedTransmitter will try to send the metrics periodically every
5 seconds or whenever the buffer remaining capacity reaches 10%, always
using a background Thread.

On some extreme cases, the BufferedTransmitter can discard old metrics.

### Implementing custom transmitters

Transmitters are pretty simple class that implements `publish` method.

```python
import json

from telemetry.metrics import Measurement
from telemetry.transmitter import Transmitter

class FileTransmitter(Transmitter):
    def publish(self, measurements):
        # measurement can be a single measurement or
        # a collection of measurement -
        # when BufferedTransmitter is being used for instance
        if isinstance(Measurement, measurements):
            measurements = [measurements]
        
        with open('metrics.txt', 'wb') as f:
            for m in measurements:
                data = {
                    'name': m.name,
                    'value': m.value,
                    'timestamp': m.timestamp,
                    'tags': m.tags
                }
                f.write(json.dumps(data))
```

## Authors

* **Danilo Queiroz**


## License

This project is licensed under the GPLv3 License - see the [LICENSE](LICENSE) file for details

