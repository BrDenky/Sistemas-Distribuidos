import zmq
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python subscriber.py <service1> [service2] [service3] ...")
        print("Available services: WEATHER, NEWS, SPORTS, FINANCE")
        print("Example: python subscriber.py WEATHER NEWS")
        sys.exit(1)
    
    # Get services to subscribe to from command line
    services = [s.upper() for s in sys.argv[1:]]
    
    # Port mapping for each service
    ports = {
        'WEATHER': 15001,
        'NEWS': 15002,
        'SPORTS': 15003,
        'FINANCE': 15004
    }
    
    # Validate services
    for service in services:
        if service not in ports:
            print(f"Invalid service: {service}")
            print(f"Available services: {', '.join(ports.keys())}")
            sys.exit(1)
    
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    
    HOST = '172.23.198.18'  # Change to publisher IP for different hosts
    
    # Connect to all requested services
    print("Subscriber starting...")
    print(f"Subscribing to services: {', '.join(services)}")
    print("-" * 60)
    
    for service in services:
        port = ports[service]
        address = f"tcp://{HOST}:{port}"
        socket.connect(address)
        # Subscribe to messages starting with service name
        socket.setsockopt_string(zmq.SUBSCRIBE, service)
        print(f"Connected to {service} service at {address}")
    
    print("-" * 60)
    print("Receiving messages (Press Ctrl+C to stop)...")
    print("-" * 60)
    
    message_count = 0
    
    try:
        while True:
            # Receive message from any subscribed service
            message = socket.recv().decode("utf-8")
            message_count += 1
            
            # Parse service type from message
            service_type = message.split()[0]
            
            print(f"[{message_count}] {message}")
    
    except KeyboardInterrupt:
        print(f"\n\nSubscriber shutting down...")
        print(f"Total messages received: {message_count}")
        socket.close()
        context.term()

if __name__ == "__main__":
    main()