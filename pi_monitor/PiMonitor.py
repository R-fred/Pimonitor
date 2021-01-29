import asyncio as aio
from dataclasses import dataclass, field
import datetime as dt
# import json as js
import os
import platform as pf
import psutil as ps
from psutil import cpu_freq, net_io_counters, swap_memory
import queue
import shutil as shu
import socket
from sys import float_repr_style, maxsize
from time import sleep
import time
import typing
from threading import Thread, Event
from typing import Dict, List, Any, Optional, Tuple

import netifaces
import orjson as js
import pika

import timeit

UNITS = {1: "B", 1024: "KB", 1024*1024: "MB", 1024*1024*1024: "GB", 1024*1024*1024*1024: "TB"}

@dataclass
class CpuData:
    logical: int = field(init=False)
    freq: Dict[str, float] = field(init=False, metadata={"unit": "MHz"})
    load: Dict[str, float] = field(init=False, metadata={"unit": "percent"})
    temp: float = field(init=False, metadata={"unit": "°C"})

    def __post_init__(self):
        self.logical = ps.cpu_count()
        cpu_freq = ps.cpu_freq(percpu=True)
        self.freq = {"current": cpu_freq[0].current, "min": cpu_freq[0].min, "max": cpu_freq[0].max}
        cpu_load = self._get_cpu_load()
        self.load = {"1min": cpu_load[0],
                         "5min": cpu_load[1],
                         "15min": cpu_load[2]}
        if ps.LINUX: # not available on windows.
            self.temp = ps.sensors_temperatures()["cpu_thermal"][0].current

    def _get_cpu_load(self):
        return [x / ps.cpu_count()*100 for x in ps.getloadavg()]

@dataclass
class TimeDeconstruct:
    year: int = field(init=False)
    month: int = field(init=False)
    day: int = field(init=False)
    hours: int = field(init=False)
    minutes: int = field(init=False)
    seconds: int = field(init=False)

    def __post_init__(self):
        t = dt.datetime.now()
        self.year = t.year
        self.month = t.month
        self.day = t.day
        self.hours = t.hour
        self.minutes = t.minute
        self.seconds = t.second

def get_timestamp(text: bool = True, unit: str = None) -> str:
    """
    unit: a unique value selected from: year, month, day, hour, minute, second.
    """
    now = dt.datetime.now()
    if text == True:
        return now.strftime("%Y.%m.%d %H:%M:%S")
    elif text == False and unit != None:
        return eval(f"now.{unit}")
    else:
        return None       

@dataclass
class TimeData:
    values: List[TimeDeconstruct] = field(default_factory=TimeDeconstruct) # how to declare dataclass in type hinting?
    string: str = field(default_factory=get_timestamp)

@dataclass
class DiskUsage:
    disk_usage: List[float] = field(default_factory=list)
    io_counters: Dict[str, int] = field(default_factory=dict)
    factor: int = 1024*1024*1024
    unit: str = field(default=None)
    
    def __post_init__(self):
        d_use = self._get_disk_usage()
        d_io = self._get_disk_io()
        self.unit = UNITS[self.factor]
        self.disk_usage = {"total": d_use[0], "used": d_use[1], "free": d_use[2]}
        self.io_counters = {"write_counters": d_io.write_count, "write_time": d_io.write_time}

    def _get_disk_usage(self):
        return [round(x / self.factor, 2) for x in ps.disk_usage("/")]

    def _get_disk_io(self):
        return ps.disk_io_counters()
    
    # def output(self):
    #     return {"disk_usage": {"total": self.disk_usage[0],
    #                            "used": self.disk_usage[1],
    #                            "free": self.disk_usage[2]},
    #             "io_counters": {"write_count": self.io_counters.write_count,
    #                             "write_time": self.io_counters.write_time}
    #             }

@dataclass
class UpTime:
    boot_time: str = field(init=False)
    uptime: Dict[str, int] = field(init=False)

    def __post_init__(self):
        data = self._get_uptime()
        self.boot_time = dt.datetime.fromtimestamp(data["boot_time"]).strftime("%Y-%m-%d %H:%M:%S")
        self.uptime = data["uptime"]

    def _get_uptime(self):
        boot = ps.boot_time()
        uptime = dt.datetime.now() - dt.datetime.fromtimestamp(boot)
        
        h, m = divmod(uptime.seconds/3600, 1)
        m, s = divmod(m*60, 1)
        s = round(s*60, 0)

        return {"boot_time":boot, "uptime": {"days": uptime.days, "hours": int(h), "minutes": int(m), "seconds": int(s)}}

@dataclass
class MemoryDataBaseClass:
    unit_fact: int = 1024*1024
    unit: str = UNITS[unit_fact]
    round_digit: int = 2

    def _get_memory_data(self):
        return None
    
    def _round_data(self, number):
        return round(number / self.unit_fact, self.round_digit)

@dataclass
class VirtualMemoryData(MemoryDataBaseClass):
    total: float = field(init=False)
    available: float = field(init=False)
    percent: float = field(init=False)
    used: float = field(init=False)
    free: float = field(init=False)
    active: float = field(init=False)
    inactive: float = field(init=False)
    buffers: float = field(init=False)
    cached: float = field(init=False)
    shared: float = field(init=False)
    slab: float = field(init=False)

    def __post_init__(self):
        virtual = self._get_memory_data()

        self.total = self._round_data(virtual.total)
        self.available = self._round_data(virtual.available)
        self.percent = virtual.percent
        self.used = self._round_data(virtual.used)
        self.free = self._round_data(virtual.free)
        if ps.LINUX: # not supported in windows
            self.active = self._round_data(virtual.active)
            self.inactive = self._round_data(virtual.inactive)
            self.buffers = self._round_data(virtual.buffers)
            self.cached = self._round_data(virtual.cached)
            self.shared = self._round_data(virtual.shared)
            self.slab = self._round_data(virtual.slab)
    
    def _get_memory_data(self):
        return ps.virtual_memory()

@dataclass
class SwapMemoryData(MemoryDataBaseClass):

    total: float = field(init=False)
    used: float = field(init=False)
    percent: float = field(init=False)
    sin: float = field(init=False)
    sout: float = field(init=False)

    def __post_init__(self):
        swap = self._get_memory_data()
        
        self.total = self._round_data(swap.total)
        self.used = self._round_data(swap.used)
        self.percent = swap.percent
        self.sin = self._round_data(swap.sin)
        self.sout = self._round_data(swap.sout)

    def _get_memory_data(self):
        return ps.swap_memory()

@dataclass
class MemoryData:
    virtual: float = field(default_factory=VirtualMemoryData)
    swap: float = field(default_factory=SwapMemoryData)

@dataclass
class PlatformData:
    hostname: str = field(init=False)
    system: Dict[str, str] = field(init=False)
    architecture: Dict[str, str] = field(init=False)
    software:Dict[str, Dict[str,str]] = field(init=False)
    basic: bool = field(default=True, )

    def __post_init__(self):
        
        uName = pf.uname()
        self.hostname = uName.node
        self.system = {"type": uName.system,
                       "kernel_version": uName.release,
                       "os_version": uName.version}
        self.architecture = self._get_architecture_info()
        self.software = self._get_software_info()
  
    def _get_architecture_info(self):
        output = {"processor_type": pf.processor()}
        if self.basic == False:
            arch = pf.architecture()
            output["bits"] = arch[0]
            output["linkage"] = arch[1]
        return output
    
    def _get_software_info(self):
        return {"python":{"version": pf.python_version(),
                          "implementation": pf.python_implementation()}
                }

@dataclass
class NetworkingData:
    monitored_ifaces: Tuple[str, str] = field(default=("eth0"))
    network_interfaces: Dict[str, str] = field(default_factory=dict)
    network_connections: Dict[str, str] = field(default_factory=dict)
    basic: bool = field(default=True)

    def __post_init__(self):
        if type(self.monitored_ifaces) == tuple:
            self.network_interfaces = {i:self._select_iface_data(i) for i in self.monitored_ifaces}
        else:
            self.network_interfaces = self._select_iface_data(iface=self.monitored_ifaces)

        if self.basic == False:   
            for cnt, elt in enumerate(ps.net_connections(), 0):
                try:
                    l = elt.laddr._asdict()
                    r = elt.raddr._asdict()
                    self.network_connections[f"{cnt}"] = {"target": l,
                                                        "incoming": r
                                                        }
                except:
                    pass
            for k, v in ps.net_if_stats().items():
                if k in self.monitored_ifaces:
                    self.network_interfaces[k]["is_up"] = v.isup
                    self.network_interfaces[k]["nicDuplex"] = v.duplex.value
                    self.network_interfaces[k]["speed"] = v.speed
                    self.network_interfaces[k]["mtu"] = v.mtu   

    def _select_iface_data(self, iface):
        if_data = netifaces.ifaddresses(iface)
        if iface in self.monitored_ifaces:
            output = {"mac_address": if_data[netifaces.AF_LINK][0]["addr"],
            "ip_address": if_data[netifaces.AF_INET][0]["addr"]}
        else:
            output = {}
        return {iface: output}

DATA_DICTIONARY = {"cpu": CpuData,
                  "platform": PlatformData,
                  "timestamp": TimeData,
                  "uptime": UpTime,
                  "virtual_memory": VirtualMemoryData,
                  "swap_memory": SwapMemoryData,
                  "networking": NetworkingData,
                  "disk": DiskUsage}

@dataclass
class PiSystemData:
    timestamp: Optional[TimeData] = field(init=False)
    uptime: Optional[UpTime] = field(init=False)
    platform: Optional[PlatformData] = field(init=False)
    cpu: Optional[CpuData] = field(init=False)
    networking: Optional[NetworkingData] = field(init=False)
    virtual_memory: Optional[VirtualMemoryData] = field(init=False)
    swap_memory: Optional[SwapMemoryData] = field(init=False)
    disk: Optional[DiskUsage] = field(init=False)

    config: List[str] = field(default=("platform", "timestamp", "uptime", "virtual_memory", "networking"))
    basic: bool = field(default=True)
    monitoredNetIfaces: str = field(default="eth0")

    def __post_init__(self): # PLACE TO DO THE ASYNC STUFF TO IMPROVE PERFORMANCE - use separate functions for setting each parameter.
        self.cpu = DATA_DICTIONARY["cpu"]()
        self.platform = DATA_DICTIONARY["platform"](basic=self.basic)
        self.timestamp = DATA_DICTIONARY["timestamp"]()
        self.uptime = DATA_DICTIONARY["uptime"]()
        self.virtual_memory = DATA_DICTIONARY["virtual_memory"]()
        self.networking = DATA_DICTIONARY["networking"](basic=self.basic,
                                         monitored_ifaces=self.monitoredNetIfaces)
        if self.basic == False:
            self.swap_memory = DATA_DICTIONARY["swap_memory"]()
            self.disk = DATA_DICTIONARY["disk"]()

### NEED SERIOUS WORK - GET INTO SEPARATE MODULE ###
class PublisherBaseClass:

    """
    Used following websites to derive this part of the code:
    :url https://github.com/pika/pika/blob/master/examples/asynchronous_publisher_example.py
    :url https://pika.readthedocs.io/en/stable/examples/connecting_async.html
    """

    def __init__(self, username: Optional[str], password: Optional[str], url: str = "localhost", publish_interval: float = 1):
        self.username = username
        self.password = password
        self.url = url
        self.publish_interval = publish_interval
    
    # Basic functionality
    def open_connection(self):
        pass

    def close_connection(self):
        pass
    
    def schedule_publish(self):
        pass

    def publish(self):
        pass
    
    # callbacks
    def on_connection_open(self):
        pass

    def on_connection_open_error(self):
        pass

    def on_connection_closed(self):
        pass

    # optional functionality
    def open_channel(self):
        pass

    def enable_delivery_confirmation(self):
        pass

    def declare_queue(self):
        pass

    def declare_exchange(self):
        pass

    def on_channel_open(self):
        pass

    def on_channel_open_error(self):
        pass

    def on_channel_closed(self):
        pass

class AMQPPublisherSimple(PublisherBaseClass):
    def __init__(self, username: str, password: str, url: str = "localhost", port: int = 5672, virtual_host: str = "/", publish_interval: float = 1.0):
        super().__init__(username, password, url, publish_interval)
        
        self.port = port
        self.virtual_host = "/"
        self._connection = None
        self._channel: Any = None
        self._queue: str = ""
        
        self._stopping = False
        self.CONNECTION_ATTEMPTS: int = 10
        self.RETRY_DELAY: float = 0.5
        self.EXCHANGE_NAME: str = ""
        self.EXCHANGE_TYPE: str = "topic"
        self.ROUTING_KEY: str = ""

        self.credentials = pika.PlainCredentials(username=self.username,
                           password=self.password,
                           erase_on_connect=True)
        self.connection_parameters = pika.ConnectionParameters(host=pika.URLParameters(self.url),
                                    port=self.port,
                                    virtual_host=self.virtual_host,
                                    credentials=self.credentials,
                                    connection_attempts= self.CONNECTION_ATTEMPTS, retry_delay=self.RETRY_DELAY)
 
    # CONNECTION
    def open_connection(self) -> None:
        self._connection = pika.SelectConnection(parameters=self.connection_parameters,
        on_open_callback=self.on_connection_open)

    def close_connection(self) -> None:
        if self._connection != None:
            self._connection.close()

    def on_connection_open(self, _unused_connection) -> None:
        self.open_channel()
    
    def on_connection_open_error(self, _unused_connection, err):
        self._connection.ioloop.call_later(2, self._connection.ioloop.stop)

    # CHANNEL
    def open_channel(self) -> None:
        self._connection.channel(on_open_callback=self.on_channel_open)

    def close_channel(self):
        if self._channel is not None:
            self._channel.close()

    def on_channel_open(self, channel) -> None:
        self._channel = channel
        self.setup_exchange(self.EXCHANGE_NAME)
    
    # EXCHANGE
    def setup_exchange(self, name) -> None:
        self._channel.exchange_declare(exchange=name, exchange_type=self.EXCHANGE_TYPE)
    
    # QUEUE
    def setup_queue(self, queue_name) -> None:
        self._channel.queue_declare(queue=queue_name, callback=self.on_queue_declareok)
    
    def on_queue_declareok(self, _unused_frame):
        self._channel.queue_bind(
            self.QUEUE,
            self.EXCHANGE_NAME,
            routing_key=self.ROUTING_KEY,
            callback=self.on_bindok)
    
    def on_bindok(self, _unused_frame) -> None:
        self.start_publishing()

    # PUBLISH
    def start_publishing(self) -> None:
        self.schedule_next_message()
    
    def schedule_next_message(self):
        self._connection.ioloop.call_later(self.publish_interval, self.publish_message)
    
    def publish_message(self) -> None:
        if self._channel is None or not self._channel.is_open:
            return

        hdrs = ""
        message = ""

        properties = pika.BasicProperties(app_id="", content_type='application/json', headers=hdrs)

        self._channel.basic_publish(self.EXCHANGE_NAME, self.ROUTING_KEY,
                                    js.dumps(message, ensure_ascii=False),
                                    properties)
        self.schedule_next_message()
    
    # RUN AND STOP
    def run(self):
        while not self._stopping:
            self._connection = None
            self._deliveries = []
            self._acked = 0
            self._nacked = 0
            self._message_number = 0

            try:
                self._connection = self.connect()
                self._connection.ioloop.start()
            except KeyboardInterrupt:
                self.stop()
                if (self._connection != None and
                        not self._connection.is_closed):
                    # Finish closing
                    self._connection.ioloop.start()

    def stop(self):
        self._stopping = True
        self.close_channel()
        self.close_connection()

class AMQPPublisher(PublisherBaseClass):
    # TODO(): Review - many issues with it.
    def __init__(self, username: str, password: str, url: str = "localhost", port: int = 5672, virtual_host: str = "/", publish_interval: float = 1.0):
        super().__init__(username, password, url, publish_interval)
        
        self.port = port
        self.virtual_host = "/"
        self._connection = None
        self._channel: Any = None
        self._queue: str = ""
        
        self._stopping = False
        self.CONNECTION_ATTEMPTS: int = 10
        self.RETRY_DELAY: float = 0.5
        self.EXCHANGE_NAME: str = ""
        self.EXCHANGE_TYPE: str = "topic"
        self.ROUTING_KEY: str = ""

        self.credentials = pika.PlainCredentials(username=self.username,
                           password=self.password,
                           erase_on_connect=True)
        self.connection_parameters = pika.ConnectionParameters(host=pika.URLParameters(self.url),
                                    port=self.port,
                                    virtual_host=self.virtual_host,
                                    credentials=self.credentials,
                                    connection_attempts= self.CONNECTION_ATTEMPTS, retry_delay=self.RETRY_DELAY)
    def open_connection(self) -> None:
        self._connection = pika.SelectConnection(parameters=self.connection_parameters,
        on_open_callback=self.on_connection_open,
        on_close_callback=self.on_connection_closed,
        on_open_error_callback=self.on_connection_open_error)

    # CONNECTION
    def close_connection(self) -> None:
        if self._connection != None:
            self._connection.close()

    def on_connection_open(self, _unused_connection) -> None:
        self.open_channel()
    
    def on_connection_open_error(self, _unused_connection, err):
        self._connection.ioloop.call_later(2, self._connection.ioloop.stop)

    # CHANNEL
    def open_channel(self) -> None:
        self._connection.channel(on_open_callback=self.on_channel_open)

    def close_channel(self):
        if self._channel is not None:
            self._channel.close()

    def on_channel_open(self, channel) -> None:
        self._channel = channel
        self.setup_exchange(self.EXCHANGE_NAME)
    
    # EXCHANGE
    def setup_exchange(self, name) -> None:
        self._channel.exchange_declare(exchange=name, exchange_type=self.EXCHANGE_TYPE)
    
    # QUEUE
    def setup_queue(self, queue_name) -> None:
        self._channel.queue_declare(queue=queue_name, callback=self.on_queue_declareok)
    
    def on_queue_declareok(self, _unused_frame):
        self._channel.queue_bind(
            self.QUEUE,
            self.EXCHANGE_NAME,
            routing_key=self.ROUTING_KEY,
            callback=self.on_bindok)
    
    def on_bindok(self, _unused_frame) -> None:
        self.start_publishing()

    # PUBLISH
    def start_publishing(self) -> None:
        self.schedule_next_message()
    
    def schedule_next_message(self):
        self._connection.ioloop.call_later(self.publish_interval, self.publish_message)
    
    def publish_message(self) -> None:
        if self._channel is None or not self._channel.is_open:
            return

        hdrs = ""
        message = ""

        properties = pika.BasicProperties(app_id="", content_type='application/json', headers=hdrs)

        self._channel.basic_publish(self.EXCHANGE_NAME, self.ROUTING_KEY,
                                    js.dumps(message, ensure_ascii=False),
                                    properties)
        self.schedule_next_message()
    
    # RUN AND STOP
    def run(self):
        while not self._stopping:
            self._connection = None
            self._deliveries = []
            self._acked = 0
            self._nacked = 0
            self._message_number = 0

            try:
                self._connection = self.connect()
                self._connection.ioloop.start()
            except KeyboardInterrupt:
                self.stop()
                if (self._connection != None and
                        not self._connection.is_closed):
                    # Finish closing
                    self._connection.ioloop.start()

    def stop(self):
        self._stopping = True
        self.close_channel()
        self.close_connection()

#####################################################

class PiMonitor:
    def __init__(self, config: Tuple[str] = ("platform", "timestamp", "uptime", "virtual_memory", "networking"),
    publish_interval: float = 10.0,
    monitor_iface: str = "eth0", send_iface: str = "eth0",
    naming: str = "ip", basic: bool = True) -> None:
        self._dataQueue = queue.Queue(maxsize=300)
        self._payloadQueue = queue.Queue(maxsize=300)
        self._Event = Event()
        self.monitored = config
        self._config = {"monitor_iface": monitor_iface,
        "send_iface": send_iface,
        "naming": naming,
        "basic": basic}
        self.publish_interval = publish_interval
        self.queue_name = self._name_msgqueue()

    def _name_msgqueue(self):
        NAMING = self._config["naming"]
        if NAMING in ("ip", "mac", "hostname"):
            NETDATA = netifaces.ifaddresses(self._config["monitor_iface"]) 
            QPFIXDICT = {"ip": NETDATA[netifaces.AF_INET][0]["addr"], "mac": NETDATA[netifaces.AF_LINK][0]["addr"], "hostname": pf.node()}
            queue_prefix = QPFIXDICT[NAMING]
        else:
            queue_prefix = pf.node()
        
        return f"{queue_prefix}_monitoring_data"
    
    def gather_data(self):
        """
        config are options to be passed to the PiSystemData class.
        """
        while not self._Event.is_set():
            qobj = PiSystemData(basic=self._config["basic"],
                   monitoredNetIfaces=self._config["monitor_iface"],
                   config=self.monitored)
            self._dataQueue.put(qobj, block=True)
            time.sleep(self.publish_interval)

    def produce_payload(self):
        while not self._Event.is_set():
                qobj = js.dumps(self._dataQueue.get(block=True))
                self._payloadQueue.put(qobj, block=True)
                # print(self._payloadQueue.qsize())

    def send(self, broker_parameters: pika.ConnectionParameters):
        while not self._Event.is_set():
            msgBody = self._payloadQueue.get(block=True) # Will wait until a payload is available to send.
            with pika.BlockingConnection(parameters=broker_parameters) as conn:
                channel = conn.channel()
                channel.queue_declare(queue=self.queue_name)
                channel.basic_publish(exchange='', routing_key=self.queue_name, body=msgBody)

    def start(self, broker_parameters: pika.ConnectionParameters):
        self.p_gather = Thread(target=self.gather_data)
        self.p_payload = Thread(target=self.produce_payload)
        self.p_send = Thread(target=self.send, args=[broker_parameters])

        try:
            self.p_gather.start()
            self.p_payload.start()
            self.p_send.start()
        except:
            print("Exiting...")

    def stop(self):
        self._Event.set()

   
# save to local DB (use LMDB? or SQLite?)
broker_cred = pika.PlainCredentials(username="ubuntu", password = "mariage23muriel08")
broker_url = "192.168.178.200"
broker_param = pika.ConnectionParameters(host=broker_url, port = 5672, virtual_host="/", credentials = broker_cred)

network_iface = netifaces.gateways()[netifaces.AF_INET][0][1]

monitor = PiMonitor(basic=True,
                    publish_interval=1/100,
                    monitor_iface=network_iface,
                    send_iface=network_iface, config = ("platform", "cpu", "timestamp", "uptime"))

monitor.start(broker_parameters=broker_param)




