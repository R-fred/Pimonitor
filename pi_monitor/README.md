# pimonitor
```pimonitor``` provides a high level API to monitor various aspects of your Raspberry pi hardware.
It abstracts calls to the platform, socket and psutil packages and tries to groups them in logical monitor units:

- CPU
- Memory
- Disk
- Process
- Uptime
- Network

All monitors can be run using one unique method ```Monitor.run()``` with *Monitor* being one of the above (see examples below).

```pimonitor``` allows to send monitoring data via a variety of mechanisms. At present the following are supported:

- File
- Sqlite DB
- Rabbitmq (using PlainCredentials, i.e. username and password)

```pimonitor``` also implements Agents to allow you to run one or more monitors at given intervals. Agents also contain the necessary logic to send messages to your desired monitoring channel.

Finally, ```pimonitor``` provides a CLI interface to monitor your Raspberry pi.


Pi monitor is hosted at:
[https://github.com/R-fred/Pimonitor](https://github.com/R-fred/Pimonitor).

Package is hosted here:
[https://test.pypi.org/search/?q=pi-monitor](https://test.pypi.org/search/?q=pi-monitor).

To install:
```python
pip install -i https://test.pypi.org/simple/ pi-monitor
```

It comes with several options to send your monitoring data to a central server for storage and processing.

Currently, you can send your monitoring data to a file or an sqlite database (see examples below).

## Usage examples

### The commandline tool
```pimonitor``` provides a simple command line tool to conviniently monitor your raspberry pi (or other computer).
It can be run like so:

```
pimonitor run --monitor cpu --monitor memory --send-to file --send-to sqlite
```

```pimonitor``` automatically generates a file or sqlite database file in the home directory of the current user.
Invoking the tool with the options above will monitor the cpu and memory and send the results to a file and sqlite database.

Or, if you want to set it up, forget it and continue your work:
```
pimonitor run --monitor cpu --monitor memory --send-to file --send-to sqlite &
```

By default, the interval between two data collection is 30 seconds. It can be adjusted like so:
```
pimonitor run --interval 5 --monitor cpu --monitor memory --send-to file --send-to sqlite &
```

The context data is by default collected once at the begining and never again. You can modify this behaviour by setting the **--refresh-context-every** option. The **--refresh-context-every** takes a float as argument. The unit is seconds.
Here is an example setting the refresh rate at 20 minut
```
pimonitor run --refresh-context-every 1200 --monitor cpu --monitor memory --send-to file --send-to sqlite &
```

You can also pass arguments to the senders. ```pimonitor``` assumes that the ```--send-to``` and ```--send-to-options``` are in the same order. Options are used as follows:

```
pimonitor run --monitor cpu --send-to rabbitmq --send-to-options '{"host": "localhost", "port": 5672, "credentials":["test", "test"]}'
```

```pimonitor``` can be stopped easily by invoking the stop command. Note that this will kill the process where pimonitor is running.
```
pimonitor kill
```

### Getting data about your Raspberry pi
Getting context data about your raspberry pi is useful, especially in industrial scenarii where your devices might be located anywhere around the globe.
Getting this data every time you run a monitor is computationally expensive. Pi Monitor defines the *ContextData* class for that.
This way, the never changing data about your Raspberry pi is collected only once at the beginning of the monitoring process.

```python
from pi_monitor.contextdata import ContextData

context = ContextData()

print(context.as_dict())

> {'ip_address': 'the current IP address of your Raspi',
> 'mac_address': 'here your Raspi mac address in hexadecimal format',
> 'localhostname': 'Raspberry1003',
> 'timestamp': 1633550807.495248,
> 'boot_time': 1633178880.0}

```

### Single monitors
```python
from time import sleep

from pi_monitor.monitor.singleMonitors import CPU


cpu_monitor = CPU()

while True:
    cpu_monitor.run()
    print(cpu_monitor.as_dict())
    sleep(1)
```

```python
from pi_monitor.monitor.singleMonitors import Process

process_monitor = Process()

process_monitor.run()

r_processes = process_monitor.running_processes()
process_monitor.process_info(r_processes[2])
```

### Monitoring agents
Monitoring agents combine the monitors (e.g. CPU, Memory) and senders.
Monitoring agents can contain as many monitors and senders as necessary.
For instance, in the example below, we create and run an agent with 3 monitors and 2 senders.

Monitors can be passed as either the class itself - ``` Agent``` - or an instance of the class like so: ``` Agent()```.

Agents are subclasses of ```threading.Thread``` and can be stopped gracefully using the ```Agent.event``` attribute or the ```.stop_agent()``` method (see below.).

```python
from time import sleep

from pi_monitor.monitor.agents import AgentBuilder
from pi_monitor.monitor.senders import SenderFactory
from pi_monitor.monitor.singleMonitors import CPU, Uptime, Process, Memory, Disk

ag_builder = AgentBuilder()
sender_builder = SenderFactory()

sqlite_sender = sender_builder.build(sender_type="sqlite", database_name="./db.sqlite")
file_sender = sender_builder.build(sender_type="file", filepath="./file.txt")

ag_builder.add_monitor(CPU)
ag_builder.add_monitor(Uptime)
ag_builder.add_monitor(Memory)

ag_builder.add_sender(sqlite_sender)
ag_builder.add_sender(file_sender)

# Build the agent object
agent = ag_builder.build()

# Start monitoring
agent.start()

sleep(10) # do things

# Stop monitoring
agent.event.set()

# alternatively stop monitoring like this:
agent.stop_agent()


```

Each agent runs in its own thread. Each monitor can be run as an agent separately as shown below. The same sender can be reused between agents.

```python
from pi_monitor.monitor.agents import AgentBuilder
from pi_monitor.monitor.senders import SenderFactory
from pi_monitor.monitor.singleMonitors import CPU, Uptime, Process, Memory, Disk

# Setup the various objects builders and factories
ag_builder = AgentBuilder()
ag_builder2 = AgentBuilder()
ag_builder3 = AgentBuilder()

sender_builder = SenderFactory()

# Prepare the individual monitors and senders
sqlite_sender = sender_builder.build(sender_type="sqlite", database_name="./db.sqlite")
file_sender = sender_builder.build(sender_type="file", filepath="./file.txt")

ag_builder.add_monitor(CPU())
ag_builder.add_sender(sqlite_sender)

ag_builder2.add_monitor(Uptime())
ag_builder2.add_sender(sqlite_sender)

ag_builder3.add_monitor(Memory())
ag_builder3.add_sender(file_sender)

# Build agent objects
agent1 = ag_builder.build()
agent2 = ag_builder2.build()
agent3 = ag_builder3.build()

# Start monitoring
agent1.start()
agent2.start()
agent3.start()

# Stop monitoring
agent1.stop_agent()
agent2.stop_agent()
agent3.stop_agent()
```

The data is stored in the database in json format according to the following schema:
```CREATE TABLE IF NOT EXISTS My_Raspberry_Pi_hostname (timestamp TEXT, context JSON, monitors TEXT, data json)```

**TODO**: database table could be simplified by keeping data together in one single *JSON* column in the database (see [here](https://stackoverflow.com/questions/58519714/how-to-extract-properly-when-sqlite-json-has-value-as-an-array))

We can now retrieve the data from the database easily.

```python
import sqlite3

conn = sqlite3.connect('./db.sqlite')
c = conn.cursor("SELECT json_extract(context, '$.ip_address', '$.mac_address') from My_Raspberry_Pi LIMIT 1")
c.fetchall()

c.execute("SELECT json_extract(context, '$.CPU.cpu_percent.cpu_percent') FROM My_Raspberry_Pi WHERE monitors LIKE '%CPU%'")
c.fetchall()

c.execute("SELECT json_extract(data, '$.CPU.timestamp') AS Timestamp, json_extract(data, '$.CPU.cpu_percent.cpu_percent') AS CPU_percent FROM My_Raspberry_Pi WHERE monitors LIKE '%CPU%'")
c.fetchall()

conn.close()
```

For more details on how to retrieve data from json data structures in sqlite read [here](https://stackoverflow.com/questions/58519714/how-to-extract-properly-when-sqlite-json-has-value-as-an-array)

### Deprecated - Compound monitors
You can create your own custom monitor using compound monitors. These can be run using the same ```.run()``` method as regular monitors.

**Deprecation notice: you can achieve the same by building an agent without senders.** Doing so comes with the nice benefit that your monitor will run in its own thread (not the case with compound monitors).

```python
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

```python
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
