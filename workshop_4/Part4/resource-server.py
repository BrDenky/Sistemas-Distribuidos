import zmq
import time

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

resource_busy = False

print("Resource manager started...")

while True:
    request = socket.recv_string()
    print("Request received:", request)

    if request == "RELEASE":
        resource_busy = False
        print("Resource released by a node.")
        socket.send_string("ACK_RELEASE")
    elif not resource_busy:
        resource_busy = True
        print("Resource granted to a node.")
        socket.send_string("GRANTED")
    else:
        print("Resource denied.")
        socket.send_string("DENIED")