from dataclasses import dataclass, field
import datetime as dt
from typing import Dict, List, NamedTuple, Optional, Any, Union

import psutil as ps
from psutil import Process as proc

from .monitorABC import IMonitor
from .utils import _utc_timestamp, get_monitor_name, FILESIZES, UpTimeData


@dataclass
class Uptime(IMonitor):
    """[summary]

    Args:
        IMonitor ([type]): [description]

    Returns:
        [type]: [description]
    """
    uptime: Union[UpTimeData, None] = None

    def __post_init__(self):
        self.mtype: str = "Uptime" # get_monitor_name(monitor=self)


    def run(self) -> IMonitor:
        try:
            self.timestamp = _utc_timestamp()
            self.boot_time = ps.boot_time()
            self.uptime = self._uptime()
            self.was_run = True
        except:
            raise
        finally:
            return self


    def as_dict(self) -> Union[Dict[str, Any], None]:
        output = None
        try:
            output = {"id": self.id,
                      "timestamp": str(dt.datetime.fromtimestamp(self.timestamp,tz=dt.timezone.utc)),
                      "boot_time": str(dt.datetime.fromtimestamp(self.boot_time)),
                      "uptime": self.uptime._asdict()}
        except:
            raise
        finally:
            return output


    def _uptime(self):
        uptime = dt.datetime.now() - dt.datetime.fromtimestamp(self.boot_time)
        
        h, m = divmod(uptime.seconds/3600, 1)
        m, s = divmod(m*60, 1)
        s = round(s*60, 0)

        return UpTimeData(days=uptime.days, hours=int(h), minutes=int(m), seconds=int(s))


@dataclass
class CPU(IMonitor):
    """[summary]

    Args:
        IMonitor ([type]): [description]

    Returns:
        [type]: [description]
    """
    average_load: Union[Dict[str, float], None] = None
    cpu_percent: Union[List[Dict[str, float]], None] = None
    per_cpu: bool = False

    def __post_init__(self):
        self.mtype: str = "CPU" # get_monitor_name(monitor=self)


    def run(self) -> IMonitor:
        # TODO: add cpu temperature check for raspberry pi.
        try:
            self.timestamp = _utc_timestamp()
            self.average_load = self._get_average_load()
            self.cpu_percent = self._get_cpu_percent()
            self.was_run = True
        except:
            raise
        finally:
            return self

  
    def as_dict(self):
        output = None
        try:
            output = {"id": self.id,
                    "timestamp": self.timestamp,
                    "cpu_percent": {"per_cpu": self.per_cpu, "cpu_percent": self.cpu_percent},
                    "average_load": self.average_load
                    }
        except:
            raise
        finally:
            return output


    def _get_cpu_percent(self) -> Union[List[Dict[str, float]], None]:
        output = None
        try:
            if self.per_cpu:
                input = [x._asdict() for x in ps.cpu_times_percent(percpu=self.per_cpu)]
                output = [{k: v for k,v in x.items() if k in ["user", "system", "idle"]} for x in input]
            if self.per_cpu == False:
                input = ps.cpu_times_percent(percpu=self.per_cpu)
                output = [input._asdict()]
        except:
            raise
        finally:
            return output


    def _get_average_load(self) -> Union[Dict[str, float], None]:
        output = None
        try:
            input_load: List[float] = [round(x / ps.cpu_count() * 100, 2) for x in ps.getloadavg()]
            output = {"1min": input_load[0], "5min": input_load[1], "15min": input_load[2]}
        except:
            raise
        finally:
            return output


@dataclass
class Memory(IMonitor):
    """[summary]

    Args:
        IMonitor ([type]): [description]

    Returns:
        [type]: [description]
    """
    virtual: Union[NamedTuple, None] = None
    swap: Union[NamedTuple, None] = None

    def __post_init__(self):
        self.mtype: str = "Memory" # get_monitor_name(monitor=self)


    def run(self) -> IMonitor:
        try:
            self.timestamp = _utc_timestamp()
            self.virtual: NamedTuple = ps.virtual_memory()
            self.swap: NamedTuple = ps.swap_memory()
            self.was_run = True
        except:
            raise
        finally:
            return self


    def as_dict(self) -> Union[dict[str, Any], None]:
        output = None
        try:
            output = {"id": self.id,
                    "timestamp": self.timestamp,
                    "virtual_memory": self.virtual._asdict(),
                    "swap": self.swap._asdict()
                    }
        except:
            raise
        finally:
            return output


@dataclass
class Disk(IMonitor):
    """[summary]

    Args:
        IMonitor ([type]): [description]

    Returns:
        [type]: [description]
    """
    mountpoint: str = "/"

    def __post_init__(self):
        self.mtype: str = "Disk" # get_monitor_name(monitor=self)


    def run(self) -> IMonitor:
        try:
            self.timestamp: float = _utc_timestamp()
            self.io_counters: NamedTuple = ps.disk_io_counters()
            self.usage: NamedTuple = ps.disk_usage(path=self.mountpoint)
            self.partitions: List[NamedTuple] = ps.disk_partitions(all=True)
            self.n_partitions: int = len(self.partitions)
            self.was_run: bool = True
        except:
            raise
        finally:
            return self


    def as_dict(self) -> Union[Dict[str, Any], None]:
        output = None
        try:
            output = {"id": self.id,
                    "timestamp": self.timestamp,
                    "io_counters": self.io_counters._asdict(),
                    "n_partitions": self.n_partitions,
                    "partitions": [p._asdict() for p in self.partitions],
                    "usage": {"mountpoint": self.mountpoint, "usage": self.usage._asdict()}
                    }
        except:
            raise
        finally:
            return output
    

@dataclass
class Process(IMonitor):
    """Class to monitor processes. Can also be used to retrieve informatiin about a running process.

    Returns:
        Process: returns a Process class
    """
    n_processes: Optional[int] = field(init=False, default=None, repr=True)
    process_list: Optional[List[int]] = field(init=False, default=None, repr=True)

    def __post_init__(self):
        self.mtype: str = "Process" # get_monitor_name(monitor=self)


    def run(self) -> IMonitor:
        try:
            self.timestamp = _utc_timestamp()
            self.process_list = self._get_process_list()
            self.n_processes = self._get_n_processes()
            self.was_run = True
        except:
            raise
        finally:
            return self


    def as_dict(self) -> Union[Dict[str, Any], None]:
        output = None
        try:
            output = {"id": self.id,
                    "timestamp": self.timestamp,
                    "process_list": self.process_list,
                    "n_processes": self.n_processes
                    }
        except:
            raise
        finally:
            return output


    def _get_n_processes(self) -> Union[int, None]:
        output = None
        try:
            output = len(self.process_list)
        except:
            raise
        finally:
            return output


    def _get_process_list(self) -> Union[List[int], None]:
        output = None
        try:
            output = ps.pids()
        except:
            raise
        finally:
            return output


    def process_info(self, pid: int) -> Union[proc, None]:
        output = None
        try:
            if pid in self.process_list:
                output = proc(pid=pid)
            
        except:
            raise
        finally:
            return output


    def running_processes(self) -> Union[List[int], None]:
        output = None
        try:
            p_list = self.process_list
            existing_processes = [pr for pr in p_list if ps.pid_exists(pr)]
            output = [e for e in existing_processes if self.process_info(e).status() == "running"]
        except:
            raise
        finally:
            return output


MONITORS = {"Uptime": Uptime, "CPU": CPU, "Memory": Memory, "Disk": Disk, "Process": Process}

# ######### QUICK TESTS #########

# print("\n----- Process Monitor ------")
# p = Process()
# p.run()
# print(type(p))
# print(p.process_list)
# print(p.running_processes())

# print("\n----- Uptime Monitor ------")
# ut = Uptime().run()
# print(ut.uptime)

# print("\n----- CPU Monitor ------")
# cp = CPU()
# cp.run()
# print(cp.average_load)
# print(cp.cpu_percent)

# print("\n----- CPU Monitor | per cpu------")
# cp2 = CPU(per_cpu=True)
# cp2.run()
# print(cp2.average_load)
# print(cp2.cpu_percent)

# print("\n----- Memory Monitor ------")
# mem = Memory()
# mem.run()
# print(mem.virtual)
# print(mem.swap)

# print("\n----- Disk Monitor ------")
# disk = Disk()
# disk.run()
# print(disk.io_counters)
# print(disk.partitions)