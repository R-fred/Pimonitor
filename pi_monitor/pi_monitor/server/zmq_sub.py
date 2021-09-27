import zmq
import time

ADDRESS = "tcp://localhost"
PORT = 5555
FULL_ADDRESS = f"{ADDRESS}:{PORT}"

context = zmq.Context()

TOPICFILTER = "raspi_monitor_xy"

socket = context.socket(zmq.SUB)
print(FULL_ADDRESS)
socket.connect(FULL_ADDRESS)
socket.setsockopt_string(zmq.SUBSCRIBE, TOPICFILTER) # subscribe to a specific topic only.
# socket.setsockopt_string(zmq.SUBSCRIBE, "")

while True:
    string = socket.recv_string()
    topic, messagedata = string.split(": ")
    print(topic, messagedata)
    # print(string)
