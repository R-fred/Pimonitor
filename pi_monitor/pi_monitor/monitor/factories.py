from typing import Optional as _Optional

from .singleMonitors import MONITORS, Uptime, CPU, Disk, Memory, Process
from ._monitorABC import IMonitor as _IMonitor

class MonitorFactory:
    """[summary]
    """
    
    @staticmethod
    def create_monitor(monitor_type: str) -> _IMonitor:
        monitor: _Optional[_IMonitor] =  None
        try:
            monitor = MONITORS[monitor_type]()
        except:
            raise
        finally:
            return monitor



##### QUICK TESTS #####

# a = MonitorFactory.create_monitor("Uptime")
# print(a.mtype)
# a.run()
# print(a.uptime)

# a = MonitorFactory.create_monitor("CPU")
# print(a.mtype)
# a.run()
# print(a.average_load)