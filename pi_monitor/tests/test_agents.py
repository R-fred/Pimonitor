from pi_monitor.monitor import AgentBuilder, CPU, Memory

builder = AgentBuilder()
builder.add_monitor(CPU)
builder.add_monitor(Memory)
builder.add_sender("FileSender")

obj = builder.build()

print(obj.monitors, obj.senders)
print(obj.monitors[0]().id)
print(type(obj))
print(type(obj.monitors[1]()))
