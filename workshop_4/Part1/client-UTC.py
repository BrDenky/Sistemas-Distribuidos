import zmq
import threading
import time
import argparse
import sys

def utc_time_client(hostname, port, client_id):
    try:
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.setsockopt(zmq.RCVTIMEO, 3000) # 3 second timeout
        socket.connect("tcp://" + hostname + ":" + port)

        print(f"[Client {client_id}] Requesting time...")
        socket.send_string("Time request")

        try:
            utc_time = socket.recv().decode('utf-8')
            print(f"[Client {client_id}] Received UTC time: {utc_time}")
        except zmq.error.Again:
            print(f"[Client {client_id}] Error: Request timed out. Server might be down.")

    except zmq.ZMQError as e:
        print(f"[Client {client_id}] ZMQ Error: {e}")
    except Exception as e:
        print(f"[Client {client_id}] Unexpected Error: {e}")
    finally:
        socket.close()
        context.term()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UTC Time Client")
    parser.add_argument("--host", type=str, default="localhost", help="Server hostname")
    parser.add_argument("--port", type=int, default=5000, help="Server port")
    parser.add_argument("--clients", type=int, default=3, help="Number of concurrent clients to run")
    args = parser.parse_args()

    if not (1024 <= args.port <= 65535):
        print("Error: Port must be between 1024 and 65535.", file=sys.stderr)
        sys.exit(1)

    c = []
    
    print(f"Starting {args.clients} clients connecting to {args.host}:{args.port}...")

    for ii in range(args.clients):
        t = threading.Thread(target=utc_time_client, args=(args.host, str(args.port), ii+1))
        c.append(t)

        t.start()
        time.sleep(1)

    for t in c:
        t.join()

    print("All clients finished.")