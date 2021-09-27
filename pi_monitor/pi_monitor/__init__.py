from .monitor.compoundMonitors import CompoundMonitor
from .monitor.factories import MonitorFactory
from .monitor.singleMonitors import CPU, Uptime, Process, Disk, Memory

##### QUICK TESTS #####

# pr = MonitorFactory.create_monitor("Process")
# pr.run()
# print(pr)