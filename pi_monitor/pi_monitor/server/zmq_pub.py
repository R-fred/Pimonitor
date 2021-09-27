import zmq
import time
import random

ADDRESS = "tcp://*"
PORT = 5555


context = zmq.Context()

socket = context.socket(zmq.PUB)
socket.bind("%s:%s" % (ADDRESS, PORT))

cnt = 0

while True:
    try:
        cpu_usage = random.randint(0,100)
        topic = "raspi_monitor_xy:"
        message = f"CPU usage {cpu_usage}%"
        socket.send_string("%s %s" % (topic, message))
        time.sleep(1)
        cnt += 1
        print(f"Topic: {topic} - Sent message # {cnt}: {message}")

    except Exception:
        raise Exception
