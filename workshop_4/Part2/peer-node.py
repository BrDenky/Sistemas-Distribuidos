import zmq
import threading
import time
import random

context = zmq.Context()

NUM_PEERS = 4 
BASE_PORT = 6000

# reloj local
local_clock = time.time()


def add_drift():
    global local_clock
    drift = random.uniform(-2, 2)
    local_clock += drift
    print(f"Clock drift applied: {drift:.2f}")


def peer_server(peer_id):

    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://*:{BASE_PORT + peer_id}")

    while True:
        message = socket.recv_json()

        if message["type"] == "time_request":
            socket.send_json({"time": local_clock})


def peer_client(peer_id):

    global local_clock

    sockets = []

    for i in range(NUM_PEERS):

        if i != peer_id:
            s = context.socket(zmq.REQ)
            # Add timeouts to avoid blocking forever if peer is not up
            s.setsockopt(zmq.RCVTIMEO, 2000)
            s.setsockopt(zmq.SNDTIMEO, 2000)
            s.connect(f"tcp://localhost:{BASE_PORT + i}")
            sockets.append((i, s))

    cycle = 0

    while True:

        times = [local_clock]

        for target_id, s in sockets:
            try:
                s.send_json({"type": "time_request"})
                reply = s.recv_json()
                times.append(reply["time"])
                print(f"Peer {peer_id} received time from Peer {target_id}")
            except zmq.error.Again:
                print(f"Peer {peer_id} could not reach Peer {target_id} (Timeout)")
            except Exception as e:
                print(f"Peer {peer_id} error with Peer {target_id}: {e}")

        avg_time = sum(times) / len(times)
        print(f"--- Cycle {cycle} ---")
        print(f"Peer {peer_id} local clock before adjustment: {local_clock:.2f}")
        print(f"Peer {peer_id} average time from {len(times)} peers: {avg_time:.2f}")

        local_clock = avg_time
        print(f"Peer {peer_id} local clock after adjustment: {local_clock}")
        cycle += 1

        k = 10

        if cycle % k == 0:
            add_drift()

        time.sleep(3)


def run_peer(peer_id):

    server_thread = threading.Thread(target=peer_server, args=(peer_id,))
    client_thread = threading.Thread(target=peer_client, args=(peer_id,))

    server_thread.start()
    client_thread.start()


if __name__ == "__main__":

    peer_id = int(input("Enter peer ID (0,1,2,3): "))

    run_peer(peer_id)

