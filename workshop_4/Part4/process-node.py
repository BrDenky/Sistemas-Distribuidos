import zmq
import time
import random
import sys

def process_node(node_id):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")

    print(f"Process Node {node_id} started. Connecting to resource server...")

    for i in range(3):
        # Wait a random time before requesting
        time.sleep(random.uniform(1, 3))
        
        print(f"[Node {node_id}] Requesting access to shared resource...")
        socket.send_string("REQUEST")
        response = socket.recv_string()

        if response == "GRANTED":
            print(f"[Node {node_id}] Access GRANTED. Working in critical section...")
            time.sleep(2) # Simulate work
            
            # Release resource
            print(f"[Node {node_id}] Work done. Releasing resource...")
            socket.send_string("RELEASE")
            ack = socket.recv_string()
            print(f"[Node {node_id}] Server response: {ack}")
        else:
            print(f"[Node {node_id}] Access DENIED. Resource is busy. Will try again later.")
            time.sleep(1)

    print(f"Process Node {node_id} finished.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        node_id = sys.argv[1]
    else:
        node_id = random.randint(100, 999)
        
    process_node(node_id)