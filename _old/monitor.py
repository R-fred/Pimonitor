import os
from time import sleep
import psutil as ps
import shutil as shu
from psutil import net_io_counters
import datetime as dt

## NETWORK

for key, value in ps.net_if_addrs().items():
    for elt in value:
        if elt.family.name == "AF_INET" and key == "eth0":
            sTring = key + ": " + elt.family.name + " " + (elt.address)
            print(f"{key} address family: {elt.family.name}.\n{key} IP address: {elt.address}\n")

# for key, value in ps.net_if_stats().items():
#     if key == "eth0":
#         print(f"etho is up: {value.isup}")

import psutil as ps
for elt in ps.net_connections():
    try:
        l = elt.laddr._asdict()
        r = elt.raddr._asdict()
        print(f'{l["ip"]}:{l["port"]} <- {r["ip"]}:{r["port"]}')
    except:
        pass

## Processes
print(f"pid | name | mem % | cpu % | uname")
for p in ps.process_iter():
    print(f"{p.pid} | {p.name()} | {p.memory_percent()} | {p.cpu_percent()} | {p.username()}")

## TEMPERATURE
print(ps.sensors_temperatures()["cpu_thermal"][0].current)

print(ps.LINUX) # USER, SSH_CLIENT, SSH_CONNECTION
## CPU
print(f"# logical CPUs: {ps.cpu_count()}")
print(f"CPU frequency: {ps.cpu_freq(percpu=True)}")
print(f"CPU percent: {ps.cpu_percent(percpu=True, interval=0.5)}")
print(f"Average CPU load (1, 5, 15 min): {os.getloadavg()}")
print(f"Average CPU load % (1, 5, 15 min): {[x / ps.cpu_count()*100 for x in os.getloadavg()]}")

## Disk usage
print([round(x / 1024 / 1024, 2) for x in ps.disk_usage("/")])

print(shu.disk_usage("/"))

print(ps.disk_io_counters().write_count)
print(ps.disk_io_counters().write_time)
with open("trial.txt", "w") as f:
    f.write("this is for a trial.")
print(ps.disk_io_counters().write_count)
print(ps.disk_io_counters().write_time)

## Last boot time
print(dt.datetime.fromtimestamp(ps.boot_time()).strftime("%Y-%m-%d %H:%M:%S"))
print(f"Boot time: {dt.datetime.fromtimestamp(ps.boot_time())}")
print(ps.swap_memory())