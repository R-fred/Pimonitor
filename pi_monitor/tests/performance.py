## CHECK CODE PERFORMANCE
REPETITIONS = 1000

# Collect data
print("Collecting data...")
r_CpuData = timeit.timeit(lambda: CpuData(), number=REPETITIONS)/REPETITIONS
print("> CpuData done.")
r_TimeData = timeit.timeit(lambda: TimeData(), number=REPETITIONS)/REPETITIONS
print("> TimeData done.")
r_TimeDeconstruct = timeit.timeit(lambda: TimeDeconstruct(), number=REPETITIONS)/REPETITIONS
print("> TimeDeconstruct done.")
r_DiskUsage = timeit.timeit(lambda: DiskUsage(), number=REPETITIONS)/REPETITIONS
print("> DiskUsage done.")
r_UpTime = timeit.timeit(lambda: UpTime(), number=REPETITIONS)/REPETITIONS
print("> UpTime done.")
r_VirtualMemoryData = timeit.timeit(lambda: VirtualMemoryData(), number=REPETITIONS)/REPETITIONS
print("> VirtualMemory done.")
r_SwapMemoryData = timeit.timeit(lambda: SwapMemoryData(), number=REPETITIONS)/REPETITIONS
print("> SwapMemory done.")
r_PlatformData = timeit.timeit(lambda: PlatformData(), number=REPETITIONS)/REPETITIONS
print("> PlatformData done.")
r_NetworkingData = timeit.timeit(lambda: NetworkingData(), number=REPETITIONS)/REPETITIONS
print("> NetworkingData done.")
r_PiSystemData = timeit.timeit(lambda: PiSystemData(), number=REPETITIONS)/REPETITIONS
print("> PiSystemData done.")
r_PiMonitor = timeit.timeit(lambda: PiMonitor(username="ubuntu", password="mariage23muriel08", basic=False), number=REPETITIONS) / REPETITIONS
print("> PiMonitor - basic = False - done.")
r_PiMonitor_basic = timeit.timeit(lambda: PiMonitor(username="ubuntu", password="mariage23muriel08", basic=True), number=REPETITIONS) / REPETITIONS
print("> PiMonitor - basic = True - done.")

# Print results:
print("#### RESULTS ####")
print(f"CpuData:\t{r_CpuData}")
print(f"TimeData:\t{r_TimeData}")
print(f"TimeDeconstruct:\t{r_TimeDeconstruct}")
print(f"DiskUsage:\t{r_DiskUsage}")
print(f"UpTime:\t{r_UpTime}")
print(f"VirtualMemoryData:\t{r_VirtualMemoryData}")
print(f"SwapMemoryData:\t{r_SwapMemoryData}")
print(f"PlatformData:\t{r_PlatformData}")
print(f"NetworkingData:\t{r_NetworkingData}")
print(f"### Sum:\t{r_CpuData + r_TimeData + r_UpTime + r_VirtualMemoryData + r_PlatformData + r_NetworkingData}")
print(f"########")
print(f"PiSystemData:\t{r_PiSystemData}")
print(f"PiMonitor - basic = True:\t{r_PiMonitor_basic}")
print(f"PiMonitor - basic = False:\t{r_PiMonitor}")

print(PiMonitor(username="ubuntu", password="mariage23muriel08", basic=True))