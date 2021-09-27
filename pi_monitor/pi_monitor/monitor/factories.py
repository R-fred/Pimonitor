from typing import Union

from .singleMonitors import MONITORS, Uptime, CPU, Disk, Memory, Process
from .monitorABC import IMonitor

class MonitorFactory:
    """[summary]
    """
    
    @staticmethod
    def create_monitor(monitor_type: str) -> IMonitor:
        monitor: Union[IMonitor, None] =  None
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