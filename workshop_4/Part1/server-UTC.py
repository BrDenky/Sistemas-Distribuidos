import zmq
import time
import argparse
import sys

def utc_time_server(port):
    try:
        context = zmq.Context()
        socket = context.socket(zmq.REP)

        socket.bind("tcp://*:" + port)

        print("UTC Time Server running...")

        while True:

            message = socket.recv()
            print("Received request:", message.decode())

            utc_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())

            socket.send_string(utc_time)

            print("Sent UTC time:", utc_time)

    except zmq.ZMQError as e:
        print(f"Server ZMQ error: {e}")
    except KeyboardInterrupt:
        print("\nServer shutting down gracefully.")
    except Exception as e:
        print(f"Unexpected server error: {e}")
    finally:
        if 'context' in locals():
            context.term()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UTC Time Server")
    parser.add_argument("--port", type=int, default=5000, help="Port to listen on (e.g., 5000)")
    args = parser.parse_args()

    if not (1024 <= args.port <= 65535):
        print("Error: Port must be between 1024 and 65535.", file=sys.stderr)
        sys.exit(1)

    utc_time_server(str(args.port))