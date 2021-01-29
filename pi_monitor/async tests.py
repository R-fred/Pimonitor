import datetime as dt
from PiMonitor import PiSystemData
import os
import psutil as ps
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor
import concurrent.futures as cf
import asyncio

import asyncio as aio
from dataclasses import dataclass, field
import datetime as dt
# import json as js
import os
import platform as pf
import psutil as ps
from psutil import cpu_freq, net_io_counters, swap_memory
import shutil as shu
import socket
from sys import float_repr_style
from time import sleep
import time
import typing
from typing import Dict, List, Any, Optional, Tuple

import netifaces
import orjson as js
import pika

import timeit

# def _get_cpu_load():
#         return [x / ps.cpu_count()*100 for x in os.getloadavg()]

# def _get_cpu_data():
#     results = {}
#     cpu_load = _get_cpu_load()
#     results["logical"] = ps.cpu_count()
#     cpu_freq = ps.cpu_freq(percpu=True)
#     results["freq"] = {"current": cpu_freq[0].current, "min": cpu_freq[0].min, "max": cpu_freq[0].max}
#     results["percent"] = ps.cpu_percent(percpu=True, interval=self.interval)
#     results["cpu_load"] = _get_cpu_load()
#     results["load"] = {"1min": cpu_load[0],
#                        "5min": cpu_load[1],
#                        "15min": cpu_load[2]}
#     results["temp"] = ps.sensors_temperatures()["cpu_thermal"][0].current

#     return results


# st = dt.datetime.now()

# RANGE = 200
# results_normal = [_get_cpu_load() for _ in range(RANGE)]  
# end = dt.datetime.now()
# duration_normal = end - st
# print(f"Normal function: {duration_normal.days} days, {duration_normal.seconds} s and {duration_normal.microseconds} ms.")

# st = dt.datetime.now()
# with ThreadPoolExecutor(max_workers=3) as executor:
#     futures = [executor.submit(_get_cpu_load) for _ in range(RANGE)]
    
#     result = [f.result() for f in cf.as_completed(futures)]
#     # for _ in range(RANGE):
#     #     futures = executor.map(_get_cpu_load)
#     # result = [f.get() for f in futures]
# end = dt.datetime.now()
# duration_normal = end - st
# print(f"Threaded: {duration_normal.days} days, {duration_normal.seconds} s and {duration_normal.microseconds} ms.")
# print(len(result))

# st = dt.datetime.now()
# with ProcessPoolExecutor(max_workers=3) as executor:
#     futures = [executor.map(_get_cpu_load) for _ in range(RANGE)]
    
#     #result = [f.result() for f in cf.as_completed(futures)]
#     # for _ in range(RANGE):
#     #     futures = executor.map(_get_cpu_load)
#     # result = [f.get() for f in futures]
# end = dt.datetime.now()
# duration_normal = end - st
# print(f"Threaded: {duration_normal.days} days, {duration_normal.seconds} s and {duration_normal.microseconds} ms.")



############################################################################
############################################################################

# from PiMonitor import CpuData, PlatformData, TimeData, UpTime, VirtualMemoryData

# st = dt.datetime.now()
# to_perform = (CpuData, PlatformData, TimeData, UpTime, VirtualMemoryData)
# result = [x for x in to_perform]
# print(f"List comprehension: {dt.datetime.now() - st} seconds")
# print(result)

# st = dt.datetime.now()
# to_perform = (CpuData, PlatformData, TimeData, UpTime, VirtualMemoryData)
# result = []
# for x in to_perform:
#     result.append(x())
# print(f"For loop: {dt.datetime.now() - st} seconds")

# st = dt.datetime.now()
# to_perform = (CpuData, PlatformData, TimeData, UpTime, VirtualMemoryData)
# to_perform[0]()
# to_perform[1]()
# to_perform[2]()
# to_perform[3]()
# to_perform[4]()
# print(f"one after the other: {dt.datetime.now() - st} seconds")

class AsyncPiSysData:
    def __await__(self):
        return PiSystemData()

async def get_data():
    return AsyncPiSysData()

async def send(): # This should work for creating the async verison of the PiSystemData class.
    task1 = asyncio.create_task(get_data())
    task2 = asyncio.create_task(asyncio.sleep(0.01))
    await task1
    await task2

st = dt.datetime.now()
asyncio.run(send())
print(f"time: {dt.datetime.now() - st} seconds")

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
        self.temp = ps.sensors_temperatures()["cpu_thermal"][0].current

    def _get_cpu_load(self):
        return [x / ps.cpu_count()*100 for x in os.getloadavg()]

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
        async def set_cpu(self):
            await DATA_DICTIONARY["cpu"]()
        async def set_cpu(self):
            pass
        self.platform = DATA_DICTIONARY["platform"](basic=self.basic)
        self.timestamp = DATA_DICTIONARY["timestamp"]()
        self.uptime = DATA_DICTIONARY["uptime"]()
        self.virtual_memory = DATA_DICTIONARY["virtual_memory"]()
        self.networking = DATA_DICTIONARY["networking"](basic=self.basic,
                                         monitored_ifaces=self.monitoredNetIfaces)
        if self.basic == False:
            self.swap_memory = DATA_DICTIONARY["swap_memory"]()
            self.disk = DATA_DICTIONARY["disk"]()