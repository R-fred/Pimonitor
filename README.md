# Pi monitor
Pi monitor provides a high level API to monitor various aspects of your Raspberry pi hardware.
It abstarcts calls to the platform, socket and psutil packages and tries to groups them in logical monitor units:

- CPU
- Memory
- Disk
- Process
- Uptime
- Network (coming soon)

All monitors can be run using one unique method ```Monitor.run()``` with *Monitor* being one of the above (see examples below).


Pi monitor is hosted at:
[https://github.com/R-fred/Pimonitor](https://github.com/R-fred/Pimonitor).

Package is hosted here:
[https://test.pypi.org/search/?q=pi-monitor](https://test.pypi.org/search/?q=pi-monitor).

To install:
```
pip install -i https://test.pypi.org/simple/ pi-monitor
```

It comes (will come :-)) with several options to send your monitoring data to a central server for storage and processing.

## Usage examples

### Getting data about your Raspberry pi
Getting context data about your raspberry pi is useful, especially in industrial scenarii where your devices might be located anywhere around the globe.
Getting this data at every run is computationally expensive. Pi Monitor defines the *ContextData* class for that.
This way, the never changing data about your Raspberry pi is collected only once at the beginning of the monitoring process.

```
from pi_monitor.contextdata import ContextData

context = ContextData()

print(context.as_dict())

```

### Single monitors
```
from time import sleep

from pi_monitor.monitor.singleMonitors import CPU


cpu_monitor = CPU()

while True:
    cpu_monitor.run()
    print(cpu_monitor.as_dict())
    sleep(1)
```

```
from pi_monitor.monitor.singleMonitors import Process
process_monitor = Process()
process_monitor.run()
r_processes = process_monitor.running_processes()
process_monitor.process_info(r_processes[2])
```

### Compound monitors
You can create your own custom monitor using compound monitors. These can be run using the same .run() method as regular monitors.

```
from time import sleep
from pi_monitor.compoundMonitors import CoumpoundMonitor as CM
from pi_monitor.monitor.singleMonitors import CPU, Uptime, Process, Memory, Disk

Monitor = CM(name="My_Monitor", monitors=[CPU(), Uptime(), Process(), Memory(), Disk()])
while True:
    CM.run()
    print(CM.as_dict())
    sleep(1)
```
Alternatively:
```
from time import sleep
from pi_monitor.compoundMonitors import CoumpoundMonitor as CM
from pi_monitor.monitor.singleMonitors import CPU, Uptime, Process, Memory, Disk

cpu = CPU()
uptime = Uptime()
proc = Process()
memory = Memory()
disk = Disk()

Monitor = CM(name="My_Monitor", monitors=[cpu, uptime, proc, memory, disk])
while True:
    CM.run()
    print(CM.as_dict())
    sleep(1)
```

### Monitoring agents
```



```