from dataclasses import dataclass as _dataclass, field as _field
import datetime as _dt
from typing import Dict as _Dict, List as _List, NamedTuple as _NamedTuple, Optional as _Optional, Any as _Any, Union as _Union

import psutil as _ps
from psutil import Process as _proc

from ._monitorABC import IMonitor as _IMonitor
from ._utils import _utc_timestamp, UpTimeData as _UpTimeData


@_dataclass
class Uptime(_IMonitor):
    """[summary]

    Args:
        IMonitor ([type]): [description]

    Returns:
        [type]: [description]
    """
    uptime: _Optional[_UpTimeData] = None

    def __post_init__(self):
        self.mtype: str = "Uptime"


    def run(self) -> _IMonitor:
        try:
            self.timestamp = _utc_timestamp()
            self.boot_time = _ps.boot_time()
            self.uptime = self._uptime()
            self.was_run = True
        except:
            raise
        finally:
            return self


    def as_dict(self) -> _Optional[_Dict[str, _Any]]:
        output = None
        try:
            output = {"id": self.id,
                      "timestamp": str(_dt.datetime.fromtimestamp(self.timestamp,tz=_dt.timezone.utc)),
                      "boot_time": str(_dt.datetime.fromtimestamp(self.boot_time)),
                      "uptime": self.uptime._asdict()}
        except:
            raise
        finally:
            return output


    def _uptime(self):
        uptime = _dt.datetime.now() - _dt.datetime.fromtimestamp(self.boot_time)
        
        h, m = divmod(uptime.seconds/3600, 1)
        m, s = divmod(m*60, 1)
        s = round(s*60, 0)

        return UpTimeData(days=uptime.days, hours=int(h), minutes=int(m), seconds=int(s))


@_dataclass
class CPU(_IMonitor):
    """[summary]

    Args:
        IMonitor ([type]): [description]

    Returns:
        [type]: [description]
    """
    average_load: _Optional[_Dict[str, float]] = None
    cpu_percent: _Optional[_List[_Dict[str, float]]] = None
    per_cpu: bool = False

    def __post_init__(self):
        self.mtype: str = "CPU"


    def run(self) -> _IMonitor:
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


    def _get_cpu_percent(self) -> _Optional[_List[_Dict[str, float]]]:
        output = None
        try:
            if self.per_cpu:
                input = [x._asdict() for x in _ps.cpu_times_percent(percpu=self.per_cpu)]
                output = [{k: v for k,v in x.items() if k in ["user", "system", "idle"]} for x in input]
            if self.per_cpu == False:
                input = _ps.cpu_times_percent(percpu=self.per_cpu)
                output = [input._asdict()]
        except:
            raise
        finally:
            return output


    def _get_average_load(self) -> _Optional[_Dict[str, float]]:
        output = None
        try:
            input_load: _List[float] = [round(x / _ps.cpu_count() * 100, 2) for x in _ps.getloadavg()]
            output = {"1min": input_load[0], "5min": input_load[1], "15min": input_load[2]}
        except:
            raise
        finally:
            return output


@_dataclass
class Memory(_IMonitor):
    """[summary]

    Args:
        IMonitor ([type]): [description]

    Returns:
        [type]: [description]
    """
    virtual: _Optional[_NamedTuple] = None
    swap: _Optional[_NamedTuple] = None

    def __post_init__(self):
        self.mtype: str = "Memory"


    def run(self) -> _IMonitor:
        try:
            self.timestamp = _utc_timestamp()
            self.virtual: _NamedTuple = _ps.virtual_memory()
            self.swap: _NamedTuple = _ps.swap_memory()
            self.was_run = True
        except:
            raise
        finally:
            return self


    def as_dict(self) -> _Optional[_Dict[str, _Any]]:
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


@_dataclass
class Disk(_IMonitor):
    """[summary]

    Args:
        IMonitor ([type]): [description]

    Returns:
        [type]: [description]
    """
    mountpoint: str = "/"

    def __post_init__(self):
        self.mtype: str = "Disk" # get_monitor_name(monitor=self)


    def run(self) -> _IMonitor:
        try:
            self.timestamp: float = _utc_timestamp()
            self.io_counters: _NamedTuple = _ps.disk_io_counters()
            self.usage: _NamedTuple = _ps.disk_usage(path=self.mountpoint)
            self.partitions: _List[_NamedTuple] = _ps.disk_partitions(all=True)
            self.n_partitions: int = len(self.partitions)
            self.was_run: bool = True
        except:
            raise
        finally:
            return self


    def as_dict(self) -> _Optional[_Dict[str, _Any]]:
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
    

@_dataclass
class Process(_IMonitor):
    """Class to monitor processes. Can also be used to retrieve informatiin about a running process.

    Returns:
        Process: returns a Process class
    """
    n_processes: _Optional[int] = None
    process_list: _Optional[_List[int]] = None

    def __post_init__(self):
        self.mtype: str = "Process"


    def run(self) -> _IMonitor:
        try:
            self.timestamp = _utc_timestamp()
            self.process_list = self._get_process_list()
            self.n_processes = self._get_n_processes()
            self.was_run = True
        except:
            raise
        finally:
            return self


    def as_dict(self) -> _Optional[_Dict[str, _Any]]:
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


    def _get_n_processes(self) -> _Optional[int]:
        output = None
        try:
            output = len(self.process_list)
        except:
            raise
        finally:
            return output


    def _get_process_list(self) -> _Optional[_List[int]]:
        output = None
        try:
            output = _ps.pids()
        except:
            raise
        finally:
            return output


    def process_info(self, pid: int) -> _Optional[_proc]:
        output = None
        try:
            if pid in self.process_list:
                output = _proc(pid=pid)
            
        except:
            raise
        finally:
            return output


    def running_processes(self) -> _Optional[_List[int]]:
        output = None
        try:
            p_list = self.process_list
            existing_processes = [pr for pr in p_list if _ps.pid_exists(pr)]
            output = [e for e in existing_processes if self.process_info(e).status() == "running"]
        except:
            raise
        finally:
            return output


_MONITORS = {"Uptime": Uptime, "CPU": CPU, "Memory": Memory, "Disk": Disk, "Process": Process}

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