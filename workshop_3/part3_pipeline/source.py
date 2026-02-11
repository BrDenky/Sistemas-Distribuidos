import zmq
import time
import pickle
import sys
import random

def main():
    if len(sys.argv) < 2:
        print("Usage: python source.py <source_id>")
        print("Example: python source.py 1")
        sys.exit(1)
    
    source_id = sys.argv[1]
    
    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    
    # Connect to broker's frontend
    BROKER_HOST = 'localhost'  # Change to broker IP for different hosts
    BROKER_PORT = 13000
    
    address = f"tcp://{BROKER_HOST}:{BROKER_PORT}"
    socket.connect(address)
    
    print("=" * 60)
    print(f"SOURCE-{source_id} STARTED")
    print("=" * 60)
    print(f"Connected to broker at {address}")
    print("Generating tasks every 2 seconds...")
    print("-" * 60)
    
    # Give broker time to start
    time.sleep(1)
    
    task_count = 0
    
    try:
        while True:
            time.sleep(2)
            
            task_count += 1
            workload = random.randint(1, 100)
            
            # Create work package
            work = {
                'source_id': source_id,
                'task_id': task_count,
                'workload': workload,
                'timestamp': time.time()
            }
            
            socket.send(pickle.dumps(work))
            
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] Sent Task #{task_count}: Workload={workload}")
    
    except KeyboardInterrupt:
        print(f"\n\nSource-{source_id} shutting down...")
        print(f"Total tasks sent: {task_count}")
        socket.close()
        context.term()

if __name__ == "__main__":
    main()
