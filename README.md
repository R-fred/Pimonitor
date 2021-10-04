# Pi monitor
Pi monitor provides a high level API to monitor various aspects of your Raspberry pi hardware.

Pi monitor is hosted at [https://github.com/R-fred/Pimonitor](https://github.com/R-fred/Pimonitor).
Package is hosted here [https://test.pypi.org/search/?q=pi-monitor](https://test.pypi.org/search/?q=pi-monitor).

To install:
```
pip install -i https://test.pypi.org/simple/ pi-monitor
```

It comes (will come :) with several options to send your monitoring data to a central server for storage and processing.

## Usage examples

### Getting data about your Raspberry pi
```

```

### Single monitors
```
from pi_monitor.monitor.singleMonitors import CPU, Memory, Disk, Process, Uptime

cpu_monitor = CPU()
cpu_monitor.run()

process_monitor = Process()
process_monitor.run()
r_processes = process_monitor.running_processes()
process_monitor.process_info(r_processes[2])
```

### Monitoring agents
```



```