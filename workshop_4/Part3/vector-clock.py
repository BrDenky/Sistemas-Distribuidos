import zmq
import threading
import time

NUM_PROCESSES = 4
BASE_PORT = 7000

context = zmq.Context()

vector_clock = [0] * NUM_PROCESSES


def server(process_id):

    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://*:{BASE_PORT + process_id}")

    while True:

        message = socket.recv_json()

        sender_clock = message["vector"]

        print(f"Process {process_id} received vector: {sender_clock}")

        # actualizar vector clock
        for i in range(NUM_PROCESSES):
            vector_clock[i] = max(vector_clock[i], sender_clock[i])

        vector_clock[process_id] += 1

        print(f"Process {process_id} updated vector: {vector_clock}")

        socket.send_json({"vector": vector_clock})


def client(process_id):

    sockets = []

    for i in range(NUM_PROCESSES):
        if i != process_id:
            s = context.socket(zmq.REQ)
            s.setsockopt(zmq.RCVTIMEO, 2000)
            s.setsockopt(zmq.SNDTIMEO, 2000)
            s.connect(f"tcp://localhost:{BASE_PORT + i}")
            sockets.append((i, s))

    while True:

        time.sleep(4)

        vector_clock[process_id] += 1

        print(f"Process {process_id} sending vector: {vector_clock}")

        for target_id, s in sockets:
            try:
                s.send_json({"vector": vector_clock})
                reply = s.recv_json()
                print(f"Process {process_id} received reply from {target_id}: {reply['vector']}")
                
                # Update vector clock based on reply
                for i in range(NUM_PROCESSES):
                    vector_clock[i] = max(vector_clock[i], reply['vector'][i])
                vector_clock[process_id] += 1
                
            except zmq.error.Again:
                print(f"Process {process_id} timeout communicating with Process {target_id}")
            except Exception as e:
                print(f"Process {process_id} error communicating with Process {target_id}: {e}")


def run_process(process_id):

    server_thread = threading.Thread(target=server, args=(process_id,))
    client_thread = threading.Thread(target=client, args=(process_id,))

    server_thread.start()
    client_thread.start()


if __name__ == "__main__":

    process_id = int(input("Enter process ID (0,1,2,3): "))

    run_process(process_id)