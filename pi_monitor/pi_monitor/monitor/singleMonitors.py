from dataclasses import dataclass as _dataclass, field as _field
import datetime as _dt
import re as _re
from typing import Dict as _Dict, List as _List, NamedTuple as _NamedTuple, Optional as _Optional, Any as _Any, Union as _Union

import psutil as _ps
from psutil import Process as _proc, virtual_memory

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


    def as_dict(self, timestamp_as_string: bool = True) -> _Optional[_Dict[str, _Any]]:
        output = None
        ts = self.timestamp
        bt = self.boot_time
        try:
            if timestamp_as_string:
                ts = str(_dt.datetime.fromtimestamp(ts))
                bt = str(_dt.datetime.fromtimestamp(bt))

            output = {"id": self.id,
                      "timestamp": ts,
                      "boot_time": bt,
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

        return _UpTimeData(days=uptime.days, hours=int(h), minutes=int(m), seconds=int(s))


    def __eq__(self, other):
        # For this class, always expect False
        if isinstance(other, Uptime):
            id_check = self.id == other.id
            boot_time_check = self.boot_time == other.boot_time
            uptime_check = self.uptime == other.uptime

            output = id_check and boot_time_check and uptime_check

            return output
        
        return False


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
    temperature: _Optional[float] = None

    def __post_init__(self):
        self.mtype: str = "CPU"


    def run(self) -> _IMonitor:
        try:
            self.timestamp = _utc_timestamp()
            self.average_load = self._get_average_load()
            self.cpu_percent = self._get_cpu_percent()

            try: # temperature check for the raspberry pi.
                f = open('/sys/class/thermal/thermal_zone0/temp', mode="r")
                temp: str = _re.findall(pattern="[0-9].*", string=f.readlines()[0])[0]
                self.temperature = int(temp)/1000
            except:
                self.temperature = None

            self.was_run = True
        except:
            raise
        finally:
            return self

  
    def as_dict(self, timestamp_as_string: bool = True) -> _Optional[_Dict[str, _Any]]:
        output = None
        ts = self.timestamp
        try:
            if timestamp_as_string:
                ts = str(_dt.datetime.fromtimestamp(ts))
            
            output = {"id": self.id,
                    "timestamp": ts,
                    "cpu_percent": {"per_cpu": self.per_cpu, "cpu_percent": self.cpu_percent},
                    "average_load": self.average_load,
                    "temperature": self.temperature
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


    def __eq__(self, other):
        if isinstance(other, CPU):
            id_check = self.id == other.id
            average_load_check = self.average_load == other.average_load
            cpu_percent_check = self.cpu_percent == other.cpu_percent 
            per_cpu_check = self.per_cpu == other.per_cpu

            output = id_check and average_load_check and cpu_percent_check and per_cpu_check

            return output
        
        return False


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


    def as_dict(self, timestamp_as_string: bool = True) -> _Optional[_Dict[str, _Any]]:
        output = None
        ts = self.timestamp

        try:
            if timestamp_as_string:
                ts = str(_dt.datetime.fromtimestamp(ts))

            output = {"id": self.id,
                    "timestamp": ts,
                    "virtual_memory": self.virtual._asdict(),
                    "swap": self.swap._asdict()
                    }
        except:
            raise
        finally:
            return output


    def __eq__(self, other):
        if isinstance(other, Memory):
            id_check = self.id == other.id
            virtual_check = self.virtual == other.virtual
            swap_check = self.swap == other.swap 

            output = id_check and virtual_check and swap_check

            return output
        
        return False


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


    def as_dict(self, timestamp_as_string: bool = True) -> _Optional[_Dict[str, _Any]]:
        output = None
        ts = self.timestamp

        try:
            if timestamp_as_string:
                ts = str(_dt.datetime.fromtimestamp(ts))

            output = {"id": self.id,
                    "timestamp": ts,
                    "io_counters": self.io_counters._asdict(),
                    "n_partitions": self.n_partitions,
                    "partitions": [p._asdict() for p in self.partitions],
                    "usage": {"mountpoint": self.mountpoint, "usage": self.usage._asdict()}
                    }
        except:
            raise
        finally:
            return output


    def __eq__(self, other):
        if isinstance(other, Disk):
            id_check = self.id == other.id
            io_counters_check = self.io_counters == other.io_counters
            n_partitions_check = self.n_partitions == other.n_partitions
            partitions_check = self.partitions == other.partitions
            usage_check = self.usage == other.usage

            output = id_check and io_counters_check and n_partitions_check and partitions_check and usage_check

            return output
        
        return False

    

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


    def as_dict(self, timestamp_as_string: bool = True) -> _Optional[_Dict[str, _Any]]:
        output = None
        ts = self.timestamp

        try:
            if timestamp_as_string:
                ts = str(_dt.datetime.fromtimestamp(ts))

            output = {"id": self.id,
                    "timestamp": ts,
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


    def __eq__(self, other):
        if isinstance(other, Process):
            id_check = self.id == other.id
            process_list_check = self.process_list == other.process_list
            n_processes_check = self.n_processes == other.n_processes

            output = id_check and process_list_check and n_processes_check
            
            return output
        
        return False


class Network(_IMonitor):
    """Class to monitor processes. Can also be used to retrieve informatiin about a running process.

    Returns:
        Process: returns a Process class
    """
    interfaces: _List[str] = ["eth0", "wlan0"]
    n_open_ports: _Optional[int] = None
    open_ports: _Optional[_List[int]] = None
    nic_addresses: _Optional[_Dict[str, _Any]] = None
    network_stats: _Optional[_Any] = None

    def __post_init__(self):
        self.mtype: str = "Network"


    def run(self) -> _IMonitor:
        try:
            self.timestamp = _utc_timestamp()
            self.open_ports = self._get_open_ports()
            self.n_open_ports = self._get_n_open_ports()
            self.nic_addresses = self._get_if_addrs()
            self.network_stats = self._get_network_statistics()
            self.was_run = True
        except:
            raise
        finally:
            return self


    def as_dict(self, timestamp_as_string: bool = True) -> _Optional[_Dict[str, _Any]]:
        output = None
        ts = self.timestamp

        try:
            if timestamp_as_string:
                ts = str(_dt.datetime.fromtimestamp(ts))

            output = {"id": self.id,
                    "timestamp": ts,
                    "open_ports": {"n_open_ports": self.n_open_ports, "open_ports": self.open_ports},
                    "interface_addresses": self.nic_addresses,
                    "statistics": self.network_stats._asdict()
                    }
        except:
            raise
        finally:
            return output


    def _get_n_open_ports(self) -> _Optional[_Dict[str, int]]:
        output = None
        try:
            output = {"tcp": len(self.open_ports["tcp"]), "udp": len(self.open_ports["udp"])}
        except:
            raise
        finally:
            return output


    def _get_open_ports(self) -> _Optional[_Dict[str, _Union[_List[int], int]]]:
        output = None
        try:
            tcp = [c.laddr.port for c in _ps.net_connections('tcp4') if c.status == 'LISTEN' and c.family == 2 and c.laddr.ip == '0.0.0.0']
            udp = [c.laddr.port for c in _ps.net_connections('udp4') if c.status == 'LISTEN' and c.family == 2 and c.laddr.ip == '0.0.0.0'] 
            
            if type(tcp) == int:
                tcp = [tcp,]
            if type(udp) == int:
                udp = [udp,]

            output = {"tcp": tcp, "udp": udp}
        except:
            raise
        finally:
            return output


    def _get_if_addrs(self) -> _Dict[str, _Any]:
        output = None

        def _get_active(v) -> _List[_Any]:
            return [i._asdict() for i in v if i.broadcast != None or i.ptp != None]

        try:
            #TODO: add the results of ps.net_if_stats() to get if interface is up, duplex and speed.
            output = {k: _get_active(v) for k, v in _ps.net_if_addrs().items()}
        except:
            raise
        finally:
            return output
    

    def _get_network_statistics(self) -> _Optional[_Any]:
        output = None

        try:
            output = _ps.net_io_counters()
        except:
            raise
        finally:
            return output


    def __eq__(self, other):
        if isinstance(other, Network):
            id_check = self.id == other.id
            open_ports_check = self.open_ports == other.open_ports
            nic_addresses_check = self.nic_addresses == other.nic_addresses
            network_stats_check = self.network_stats == other.network_stats

            output = id_check and nic_addresses_check and open_ports_check and network_stats_check
            
            return output
        
        return False


_MONITORS = {"uptime": Uptime, "cpu": CPU, "memory": Memory, "disk": Disk, "process": Process, "network": Network}

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
# cp2 = CPU()

# print(cp == cp2)
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

# print("\n----- Network Monitor ---")
# network = Network()
# network.run()
# print(network.as_dict())