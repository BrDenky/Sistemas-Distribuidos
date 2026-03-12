import zmq
import threading
import time
import sys
import random

NUM_NODES = 4
BASE_PORT = 8000

def token_ring_server(node_id, token_state):
    """Listens for the token from the previous node in the ring."""
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://*:{BASE_PORT + node_id}")

    print(f"[Node {node_id}] Listening on port {BASE_PORT + node_id}...")

    while True:
        message = socket.recv_string()
        if message == "TOKEN":
            token_state["has_token"] = True
            socket.send_string("ACK")
            
            # Use Token
            print(f"\n[Node {node_id}] -------- TOKEN RECEIVED --------")
            print(f"[Node {node_id}] Entering critical section...")
            time.sleep(random.uniform(1, 2)) # Simulate work
            print(f"[Node {node_id}] Leaving critical section.")
            print(f"[Node {node_id}] ----------------------------------\n")
            
            token_state["has_token"] = False
            token_state["send_token"] = True


def token_ring_client(node_id, token_state):
    """Sends the token to the next node in the ring."""
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    next_node = (node_id + 1) % NUM_NODES
    socket.connect(f"tcp://localhost:{BASE_PORT + next_node}")

    while True:
        if token_state["send_token"]:
            time.sleep(1) # Small delay before passing
            try:
                print(f"[Node {node_id}] Passing token to Node {next_node}...")
                socket.send_string("TOKEN")
                socket.recv_string() # Wait for ACK
                token_state["send_token"] = False
            except Exception as e:
                print(f"[Node {node_id}] Error passing token: {e}")
                time.sleep(2)
        else:
            time.sleep(0.5)


def run_node(node_id, has_initial_token=False):
    token_state = {"has_token": has_initial_token, "send_token": has_initial_token}

    server_thread = threading.Thread(target=token_ring_server, args=(node_id, token_state))
    client_thread = threading.Thread(target=token_ring_client, args=(node_id, token_state))

    server_thread.start()
    
    # Wait to ensure all servers are up before starting the client ring passing
    time.sleep(2)
    client_thread.start()
    
    server_thread.join()
    client_thread.join()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        node_id = int(sys.argv[1])
    else:
        node_id = int(input(f"Enter node ID (0 to {NUM_NODES - 1}): "))

    if not (0 <= node_id < NUM_NODES):
        print(f"Error: Node ID must be between 0 and {NUM_NODES - 1}")
        sys.exit(1)

    has_initial_token = (node_id == 0) # Node 0 starts with the token
    if has_initial_token:
        print(f"[Node {node_id}] Starting with the token.")

    run_node(node_id, has_initial_token)
