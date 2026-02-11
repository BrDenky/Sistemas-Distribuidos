import zmq
import pickle
import time

def main():
    context = zmq.Context()
    
    # Frontend socket for receiving from sources (PULL)
    frontend = context.socket(zmq.PULL)
    FRONTEND_PORT = 13000
    frontend.bind(f"tcp://*:{FRONTEND_PORT}")
    
    # Backend socket for sending to workers (PUSH)
    backend = context.socket(zmq.PUSH)
    BACKEND_PORT = 14000
    backend.bind(f"tcp://*:{BACKEND_PORT}")
    
    print("=" * 60)
    print("BROKER STARTED")
    print("=" * 60)
    print(f"Frontend (receiving from sources): tcp://*:{FRONTEND_PORT}")
    print(f"Backend (sending to workers): tcp://*:{BACKEND_PORT}")
    print("-" * 60)
    print("Broker is running... (Press Ctrl+C to stop)")
    print("-" * 60)
    
    message_count = 0
    
    try:
        while True:
            # Receive work from any source
            work = pickle.loads(frontend.recv())
            message_count += 1
            
            source_id = work['source_id']
            workload = work['workload']
            task_id = work['task_id']
            timestamp = time.strftime("%H:%M:%S")
            
            print(f"[{message_count}] [{timestamp}] Received from Source-{source_id}: "
                  f"Task #{task_id}, Workload={workload}")
            
            # Forward work to workers
            backend.send(pickle.dumps(work))
            print(f"    → Forwarded to workers")
    
    except KeyboardInterrupt:
        print(f"\n\nBroker shutting down...")
        print(f"Total messages processed: {message_count}")
        frontend.close()
        backend.close()
        context.term()

if __name__ == "__main__":
    main()
