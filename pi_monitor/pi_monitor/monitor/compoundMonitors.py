import asyncio
import datetime as dt
from typing import Optional, List, Union, Dict, Any

from .monitorABC import IMonitor
from .utils import _utc_timestamp, _uuid, get_monitor_name

class CompoundMonitor(IMonitor):
    """Class to monitor several aspects of the computer
    """
    def __init__(self, name: Optional[None] = None, monitors: Optional[List[IMonitor]] = None, was_run: bool = False) -> None:
        
        super().__init__()
        
        self.name = name
        self.monitors: Dict[str, IMonitor] = {}

        if monitors != None:
            if type(monitors) != list:
                monitors = [monitors]
            
            self.add_monitor(monitors=monitors)
        
        self.n_monitors: int = len(self.monitors.keys())
    
    def add_monitor(self, monitors: Union[IMonitor, List[IMonitor]]) -> None:
        try:
            if type(monitors) != list:
                monitors = [monitors]
            
            for m in monitors:
                self.monitors[m.mtype] = m
        except:
            raise

    def as_dict(self) -> Dict[str, Any]:
        output = {}
        try:
            output = {"id": self.id,
                    "name": self.name,
                    "timestamp": str(dt.datetime.fromtimestamp(self.timestamp)),
                    "monitor_data": [self.get_monitor_data(name=k) for k in self.monitors.keys()]}
        except:
            raise
        finally:
            return output
    
    def get_monitor_data(self, name: str) -> Dict[str, Any]:
        output = {}
        try:
            output[name] = self.monitors[name].as_dict()
        except:
            raise
        finally:
            return output

    def run(self) :
        try:
            self.timestamp = _utc_timestamp()
            for k, v in self.monitors.items():
                self.monitors[k] = v.run()
            self.was_run = True
        except:
            raise
        finally:
            return self


# from singleMonitors import Uptime, Disk, Process, Memory, CPU

# cm = CompoundMonitor(name="My_Monitor", monitors=[CPU(), Uptime(), Process(), Memory(), Disk()])
# cm.run()
# print(cm.timestamp)
# print(cm.monitors["CPU"].timestamp)
# print(cm.id, cm.timestamp)
# import time
# print("sleeping for 2 seconds")
# time.sleep(2)
# cm.run()
# print(cm.timestamp)
# print(cm.monitors["CPU"].timestamp)
# print(cm.n_monitors)
