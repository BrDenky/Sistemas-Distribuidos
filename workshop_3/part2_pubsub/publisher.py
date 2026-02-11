import zmq
import time
import sys
import random

def main():
    if len(sys.argv) < 2:
        print("Usage: python publisher.py <service_type>")
        print("Service types: WEATHER, NEWS, SPORTS, FINANCE")
        sys.exit(1)
    
    service_type = sys.argv[1].upper()
    
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    
    # Each publisher uses a different port based on service
    ports = {
        'WEATHER': 15001,
        'NEWS': 15002,
        'SPORTS': 15003,
        'FINANCE': 15004
    }
    
    if service_type not in ports:
        print(f"Invalid service type. Choose from: {', '.join(ports.keys())}")
        sys.exit(1)
    
    HOST = 'localhost'  # Change to '0.0.0.0' for different hosts
    PORT = ports[service_type]
    
    address = f"tcp://{HOST}:{PORT}"
    socket.bind(address)
    
    print(f"Publisher started for {service_type} service on {address}")
    print("Publishing messages every 3 seconds...")
    print("-" * 60)
    
    # Give subscribers time to connect
    time.sleep(1)
    
    # Service-specific message generators
    def generate_weather():
        temps = random.randint(15, 35)
        conditions = random.choice(['Sunny', 'Cloudy', 'Rainy', 'Windy'])
        return f"Temperature: {temps}°C, Condition: {conditions}"
    
    def generate_news():
        topics = ['Politics', 'Technology', 'Science', 'World']
        topic = random.choice(topics)
        return f"Breaking news in {topic}: Important event occurred"
    
    def generate_sports():
        teams = ['Team A', 'Team B', 'Team C', 'Team D']
        team1, team2 = random.sample(teams, 2)
        score1, score2 = random.randint(0, 5), random.randint(0, 5)
        return f"{team1} {score1} - {score2} {team2}"
    
    def generate_finance():
        stocks = ['AAPL', 'GOOGL', 'MSFT', 'AMZN']
        stock = random.choice(stocks)
        price = random.uniform(100, 500)
        change = random.uniform(-5, 5)
        return f"{stock}: ${price:.2f} ({change:+.2f}%)"
    
    generators = {
        'WEATHER': generate_weather,
        'NEWS': generate_news,
        'SPORTS': generate_sports,
        'FINANCE': generate_finance
    }
    
    message_count = 0
    
    try:
        while True:
            time.sleep(3)
            
            # Generate service-specific content
            content = generators[service_type]()
            timestamp = time.strftime("%H:%M:%S")
            
            # Message format: "SERVICE_TYPE content"
            message = f"{service_type} [{timestamp}] {content}"
            
            socket.send(message.encode("utf-8"))
            message_count += 1
            
            print(f"[{message_count}] Published: {message}")
    
    except KeyboardInterrupt:
        print(f"\n{service_type} Publisher shutting down...")
        socket.close()
        context.term()

if __name__ == "__main__":
    main()
