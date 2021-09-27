import statistics as stat
import textwrap
import timeit

# TODO: Create test performance class with report creation (json).

# GLOBAL SETUP
NUMBER = 10000
REPETITIONS = 10
CONVERT_TO_MICROSECOND = 1000000


print("\n------------------------------------")
print("\n-------- GENERATE MONITORS ---------")
print("\n------------------------------------")

# ContextData
NAME = "ContextData"
STATEMENT = "ContextData()"
SETUP = "from contextdata import ContextData"
res = [timeit.timeit(stmt=STATEMENT, number=NUMBER, setup=SETUP) for _ in range(REPETITIONS)]
mean_time_per_run = round(stat.mean(res)/NUMBER*CONVERT_TO_MICROSECOND, 2)
median_time_per_run = round(stat.median(res)/NUMBER*CONVERT_TO_MICROSECOND, 2)
stdev_repetitions = round(stat.stdev(res)/NUMBER*CONVERT_TO_MICROSECOND, 2)
stdev_repetitions_perc = round(stdev_repetitions/mean_time_per_run*100, 2)

print(f"""
Monitor: {NAME}
Test: {STATEMENT}

Number of repetitions: {REPETITIONS}
Runs per repetition: {NUMBER}

Mean time per run (us): {mean_time_per_run}
Median time per run (us): {median_time_per_run}
Standard deviation between runs (us): {stdev_repetitions}
Standard deviation between runs (%): {stdev_repetitions_perc}

""")


# Uptime
NAME = "Uptime"
STATEMENT = "Uptime().run()"
SETUP = "from singleMonitors import Uptime"
res = [timeit.timeit(stmt=STATEMENT, number=NUMBER, setup=SETUP) for _ in range(REPETITIONS)]
mean_time_per_run = round(stat.mean(res)/NUMBER*CONVERT_TO_MICROSECOND, 2)
median_time_per_run = round(stat.median(res)/NUMBER*CONVERT_TO_MICROSECOND, 2)
stdev_repetitions = round(stat.stdev(res)/NUMBER*CONVERT_TO_MICROSECOND, 2)
stdev_repetitions_perc = round(stdev_repetitions/mean_time_per_run*100, 2)

print(f"""
Monitor: {NAME}
Test: {STATEMENT}

Number of repetitions: {REPETITIONS}
Runs per repetition: {NUMBER}

Mean time per run (us): {mean_time_per_run}
Median time per run (us): {median_time_per_run}
Standard deviation between runs (us): {stdev_repetitions}
Standard deviation between runs (%): {stdev_repetitions_perc}

""")

# CPU
NAME = "CPU"
STATEMENT = "CPU().run()"
SETUP = "from singleMonitors import CPU"
res = [timeit.timeit(stmt=STATEMENT, number=NUMBER, setup=SETUP) for _ in range(REPETITIONS)]
mean_time_per_run = round(stat.mean(res)/NUMBER*CONVERT_TO_MICROSECOND, 2)
median_time_per_run = round(stat.median(res)/NUMBER*CONVERT_TO_MICROSECOND, 2)
stdev_repetitions = round(stat.stdev(res)/NUMBER*CONVERT_TO_MICROSECOND, 2)
stdev_repetitions_perc = round(stdev_repetitions/mean_time_per_run*100, 2)

print(f"""
Monitor: {NAME}
Test: {STATEMENT}

Number of repetitions: {REPETITIONS}
Runs per repetition: {NUMBER}

Mean time per run (us): {mean_time_per_run}
Median time per run (us): {median_time_per_run}
Standard deviation between runs (us): {stdev_repetitions}
Standard deviation between runs (%): {stdev_repetitions_perc}

""")

NAME = "CPU - per cpu"
STATEMENT = "CPU(per_cpu=True).run()"
SETUP = "from singleMonitors import CPU"
res = [timeit.timeit(stmt=STATEMENT, number=NUMBER, setup=SETUP) for _ in range(REPETITIONS)]
mean_time_per_run = round(stat.mean(res)/NUMBER*CONVERT_TO_MICROSECOND, 2)
median_time_per_run = round(stat.median(res)/NUMBER*CONVERT_TO_MICROSECOND, 2)
stdev_repetitions = round(stat.stdev(res)/NUMBER*CONVERT_TO_MICROSECOND, 2)
stdev_repetitions_perc = round(stdev_repetitions/mean_time_per_run*100, 2)

print(f"""
Monitor: {NAME}
Test: {STATEMENT}

Number of repetitions: {REPETITIONS}
Runs per repetition: {NUMBER}

Mean time per run (us): {mean_time_per_run}
Median time per run (us): {median_time_per_run}
Standard deviation between runs (us): {stdev_repetitions}
Standard deviation between runs (%): {stdev_repetitions_perc}

""")

# Process
NAME = "Process"
STATEMENT = "Process().run()"
SETUP = "from singleMonitors import Process"
res = [timeit.timeit(stmt=STATEMENT, number=NUMBER, setup=SETUP) for _ in range(REPETITIONS)]
mean_time_per_run = round(stat.mean(res)/NUMBER*CONVERT_TO_MICROSECOND, 2)
median_time_per_run = round(stat.median(res)/NUMBER*CONVERT_TO_MICROSECOND, 2)
stdev_repetitions = round(stat.stdev(res)/NUMBER*CONVERT_TO_MICROSECOND, 2)
stdev_repetitions_perc = round(stdev_repetitions/mean_time_per_run*100, 2)

print(f"""
Monitor: {NAME}
Test: {STATEMENT}

Number of repetitions: {REPETITIONS}
Runs per repetition: {NUMBER}

Mean time per run (us): {mean_time_per_run}
Median time per run (us): {median_time_per_run}
Standard deviation between runs (us): {stdev_repetitions}
Standard deviation between runs (%): {stdev_repetitions_perc}

""")

# Memory
NAME = "Memory"
STATEMENT = "Memory().run()"
SETUP = "from singleMonitors import Memory"
res = [timeit.timeit(stmt=STATEMENT, number=NUMBER, setup=SETUP) for _ in range(REPETITIONS)]
mean_time_per_run = round(stat.mean(res)/NUMBER*CONVERT_TO_MICROSECOND, 2)
median_time_per_run = round(stat.median(res)/NUMBER*CONVERT_TO_MICROSECOND, 2)
stdev_repetitions = round(stat.stdev(res)/NUMBER*CONVERT_TO_MICROSECOND, 2)
stdev_repetitions_perc = round(stdev_repetitions/mean_time_per_run*100, 2)

print(f"""
Monitor: {NAME}
Test: {STATEMENT}

Number of repetitions: {REPETITIONS}
Runs per repetition: {NUMBER}

Mean time per run (us): {mean_time_per_run}
Median time per run (us): {median_time_per_run}
Standard deviation between runs (us): {stdev_repetitions}
Standard deviation between runs (%): {stdev_repetitions_perc}

""")

# Compound Monitor
NAME = "CompoundMonitor"
STATEMENT = "CompoundMonitor(name='My_monitor', monitors=[CPU(), Uptime(), Disk(), Memory(), Process()]).run()"
SETUP = textwrap.dedent("""
from compoundMonitors import CompoundMonitor
from singleMonitors import CPU, Uptime, Disk, Memory, Process
""")
res = [timeit.timeit(stmt=STATEMENT, number=NUMBER, setup=SETUP) for _ in range(REPETITIONS)]
mean_time_per_run = round(stat.mean(res)/NUMBER*CONVERT_TO_MICROSECOND, 2)
median_time_per_run = round(stat.median(res)/NUMBER*CONVERT_TO_MICROSECOND, 2)
stdev_repetitions = round(stat.stdev(res)/NUMBER*CONVERT_TO_MICROSECOND, 2)
stdev_repetitions_perc = round(stdev_repetitions/mean_time_per_run*100, 2)

print(f"""
Monitor: {NAME}
Test: {STATEMENT}

Number of repetitions: {REPETITIONS}
Runs per repetition: {NUMBER}

Mean time per run (us): {mean_time_per_run}
Median time per run (us): {median_time_per_run}
Standard deviation between runs (us): {stdev_repetitions}
Standard deviation between runs (%): {stdev_repetitions_perc}

""")

print("\n------------------------------------")
print("\n------ GENERATE DICTIONARIES -------")
print("\n------------------------------------")

# ContextData
NAME = "ContextData"
STATEMENT = "ContextData().as_dict()"
SETUP = "from contextdata import ContextData"
res = [timeit.timeit(stmt=STATEMENT, number=NUMBER, setup=SETUP) for _ in range(REPETITIONS)]
mean_time_per_run = round(stat.mean(res)/NUMBER*CONVERT_TO_MICROSECOND, 2)
median_time_per_run = round(stat.median(res)/NUMBER*CONVERT_TO_MICROSECOND, 2)
stdev_repetitions = round(stat.stdev(res)/NUMBER*CONVERT_TO_MICROSECOND, 2)
stdev_repetitions_perc = round(stdev_repetitions/mean_time_per_run*100, 2)

print(f"""
Monitor: {NAME}
Test: {STATEMENT}

Number of repetitions: {REPETITIONS}
Runs per repetition: {NUMBER}

Mean time per run (us): {mean_time_per_run}
Median time per run (us): {median_time_per_run}
Standard deviation between runs (us): {stdev_repetitions}
Standard deviation between runs (%): {stdev_repetitions_perc}

""")


# Uptime
NAME = "Uptime"
STATEMENT = "Uptime().run().as_dict()"
SETUP = "from singleMonitors import Uptime"
res = [timeit.timeit(stmt=STATEMENT, number=NUMBER, setup=SETUP) for _ in range(REPETITIONS)]
mean_time_per_run = round(stat.mean(res)/NUMBER*CONVERT_TO_MICROSECOND, 2)
median_time_per_run = round(stat.median(res)/NUMBER*CONVERT_TO_MICROSECOND, 2)
stdev_repetitions = round(stat.stdev(res)/NUMBER*CONVERT_TO_MICROSECOND, 2)
stdev_repetitions_perc = round(stdev_repetitions/mean_time_per_run*100, 2)

print(f"""
Monitor: {NAME}
Test: {STATEMENT}

Number of repetitions: {REPETITIONS}
Runs per repetition: {NUMBER}

Mean time per run (us): {mean_time_per_run}
Median time per run (us): {median_time_per_run}
Standard deviation between runs (us): {stdev_repetitions}
Standard deviation between runs (%): {stdev_repetitions_perc}

""")

# CPU
NAME = "CPU"
STATEMENT = "CPU().run().as_dict()"
SETUP = "from singleMonitors import CPU"
res = [timeit.timeit(stmt=STATEMENT, number=NUMBER, setup=SETUP) for _ in range(REPETITIONS)]
mean_time_per_run = round(stat.mean(res)/NUMBER*CONVERT_TO_MICROSECOND, 2)
median_time_per_run = round(stat.median(res)/NUMBER*CONVERT_TO_MICROSECOND, 2)
stdev_repetitions = round(stat.stdev(res)/NUMBER*CONVERT_TO_MICROSECOND, 2)
stdev_repetitions_perc = round(stdev_repetitions/mean_time_per_run*100, 2)

print(f"""
Monitor: {NAME}
Test: {STATEMENT}

Number of repetitions: {REPETITIONS}
Runs per repetition: {NUMBER}

Mean time per run (us): {mean_time_per_run}
Median time per run (us): {median_time_per_run}
Standard deviation between runs (us): {stdev_repetitions}
Standard deviation between runs (%): {stdev_repetitions_perc}

""")

NAME = "CPU - per cpu"
STATEMENT = "CPU(per_cpu=True).run().as_dict()"
SETUP = "from singleMonitors import CPU"
res = [timeit.timeit(stmt=STATEMENT, number=NUMBER, setup=SETUP) for _ in range(REPETITIONS)]
mean_time_per_run = round(stat.mean(res)/NUMBER*CONVERT_TO_MICROSECOND, 2)
median_time_per_run = round(stat.median(res)/NUMBER*CONVERT_TO_MICROSECOND, 2)
stdev_repetitions = round(stat.stdev(res)/NUMBER*CONVERT_TO_MICROSECOND, 2)
stdev_repetitions_perc = round(stdev_repetitions/mean_time_per_run*100, 2)

print(f"""
Monitor: {NAME}
Test: {STATEMENT}

Number of repetitions: {REPETITIONS}
Runs per repetition: {NUMBER}

Mean time per run (us): {mean_time_per_run}
Median time per run (us): {median_time_per_run}
Standard deviation between runs (us): {stdev_repetitions}
Standard deviation between runs (%): {stdev_repetitions_perc}

""")

# Process
NAME = "Process"
STATEMENT = "Process().run().as_dict()"
SETUP = "from singleMonitors import Process"
res = [timeit.timeit(stmt=STATEMENT, number=NUMBER, setup=SETUP) for _ in range(REPETITIONS)]
mean_time_per_run = round(stat.mean(res)/NUMBER*CONVERT_TO_MICROSECOND, 2)
median_time_per_run = round(stat.median(res)/NUMBER*CONVERT_TO_MICROSECOND, 2)
stdev_repetitions = round(stat.stdev(res)/NUMBER*CONVERT_TO_MICROSECOND, 2)
stdev_repetitions_perc = round(stdev_repetitions/mean_time_per_run*100, 2)

print(f"""
Monitor: {NAME}
Test: {STATEMENT}

Number of repetitions: {REPETITIONS}
Runs per repetition: {NUMBER}

Mean time per run (us): {mean_time_per_run}
Median time per run (us): {median_time_per_run}
Standard deviation between runs (us): {stdev_repetitions}
Standard deviation between runs (%): {stdev_repetitions_perc}

""")

# Memory
NAME = "Memory"
STATEMENT = "Memory().run().as_dict()"
SETUP = "from singleMonitors import Memory"
res = [timeit.timeit(stmt=STATEMENT, number=NUMBER, setup=SETUP) for _ in range(REPETITIONS)]
mean_time_per_run = round(stat.mean(res)/NUMBER*CONVERT_TO_MICROSECOND, 2)
median_time_per_run = round(stat.median(res)/NUMBER*CONVERT_TO_MICROSECOND, 2)
stdev_repetitions = round(stat.stdev(res)/NUMBER*CONVERT_TO_MICROSECOND, 2)
stdev_repetitions_perc = round(stdev_repetitions/mean_time_per_run*100, 2)

print(f"""
Monitor: {NAME}
Test: {STATEMENT}

Number of repetitions: {REPETITIONS}
Runs per repetition: {NUMBER}

Mean time per run (us): {mean_time_per_run}
Median time per run (us): {median_time_per_run}
Standard deviation between runs (us): {stdev_repetitions}
Standard deviation between runs (%): {stdev_repetitions_perc}

""")