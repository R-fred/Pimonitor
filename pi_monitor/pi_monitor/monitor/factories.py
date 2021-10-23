from typing import Optional as _Optional

from .singleMonitors import _MONITORS, Uptime, CPU, Disk, Memory, Process
from ._monitorABC import IMonitor as _IMonitor

class MonitorFactory:
    """[summary]
    """
    
    @staticmethod
    def create_monitor(monitor_type: str) -> _IMonitor:
        monitor: _Optional[_IMonitor] =  None
        try:
            monitor = _MONITORS[monitor_type]()
        except:
            raise
        finally:
            return monitor