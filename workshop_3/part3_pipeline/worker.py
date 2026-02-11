import zmq
import time
import pickle
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python worker.py <worker_id>")
        print("Example: python worker.py 1")
        sys.exit(1)
    
    worker_id = sys.argv[1]
    
    context = zmq.Context()
    socket = context.socket(zmq.PULL)
    
    # Connect to broker's backend
    BROKER_HOST = 'localhost'  # Change to broker IP for different hosts
    BROKER_PORT = 14000
    
    address = f"tcp://{BROKER_HOST}:{BROKER_PORT}"
    socket.connect(address)
    
    print("=" * 60)
    print(f"WORKER-{worker_id} STARTED")
    print("=" * 60)
    print(f"Connected to broker at {address}")
    print("Waiting for tasks...")
    print("-" * 60)
    
    task_count = 0
    
    try:
        while True:
            # Receive work from broker
            work = pickle.loads(socket.recv())
            task_count += 1
            
            source_id = work['source_id']
            task_id = work['task_id']
            workload = work['workload']
            
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] Task #{task_count} received from Source-{source_id} "
                  f"(Task #{task_id}): Workload={workload}")
            
            # Simulate work processing (workload * 0.01 seconds)
            processing_time = workload * 0.01
            print(f"    Processing... (estimated {processing_time:.2f}s)")
            time.sleep(processing_time)
            
            print(f"    ✓ Completed!")
    
    except KeyboardInterrupt:
        print(f"\n\nWorker-{worker_id} shutting down...")
        print(f"Total tasks processed: {task_count}")
        socket.close()
        context.term()

if __name__ == "__main__":
    main()
