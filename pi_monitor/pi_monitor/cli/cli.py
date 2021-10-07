from rich.console import Console
from rich.progress import track
from time import sleep
import time

from pi_monitor.monitor.singleMonitors import CPU, Memory, Process, Uptime, Disk

console = Console()

monitors = [CPU(), Memory(), Process(), Uptime(), Disk()]

s = time.perf_counter()
for m in track(monitors, f"Running monitors..."):
    m.run()
    # sleep(2)
    # console.print(m.as_dict())
e = time.perf_counter()

console.print(f"Total: {(e - s)*1000} milliseconds")
