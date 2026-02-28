import zmq
import time
import sys
import random
import socket
import argparse
import ldap_client


# ---------------------------------------------------------------------------
# Service configuration
# ---------------------------------------------------------------------------
DEFAULT_PORTS = {
    'WEATHER': 15001,
    'NEWS':    15002,
    'SPORTS':  15003,
    'FINANCE': 15004,
}

SERVICE_DESCRIPTIONS = {
    'WEATHER': 'Real-time weather temperature and conditions',
    'NEWS':    'Breaking news across Politics, Technology, Science, World',
    'SPORTS':  'Live sports scores and team matchups',
    'FINANCE': 'Stock prices and market changes',
}


# ---------------------------------------------------------------------------
# Message generators
# ---------------------------------------------------------------------------
def generate_weather():
    temp = random.randint(15, 35)
    cond = random.choice(['Sunny', 'Cloudy', 'Rainy', 'Windy'])
    return f"Temperature: {temp}°C, Condition: {cond}"

def generate_news():
    topic = random.choice(['Politics', 'Technology', 'Science', 'World'])
    return f"Breaking news in {topic}: Important event occurred"

def generate_sports():
    teams = ['Team A', 'Team B', 'Team C', 'Team D']
    t1, t2 = random.sample(teams, 2)
    s1, s2 = random.randint(0, 5), random.randint(0, 5)
    return f"{t1} {s1} - {s2} {t2}"

def generate_finance():
    stock  = random.choice(['AAPL', 'GOOGL', 'MSFT', 'AMZN'])
    price  = random.uniform(100, 500)
    change = random.uniform(-5, 5)
    return f"{stock}: ${price:.2f} ({change:+.2f}%)"

GENERATORS = {
    'WEATHER': generate_weather,
    'NEWS':    generate_news,
    'SPORTS':  generate_sports,
    'FINANCE': generate_finance,
}


# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="ZeroMQ Publisher with LDAP registration")
    parser.add_argument("service_type",
                        choices=list(DEFAULT_PORTS.keys()),
                        type=str.upper,
                        help="Service to publish (WEATHER, NEWS, SPORTS, FINANCE)")
    parser.add_argument("--port", type=int, default=None,
                        help="Port to bind on (default: per-service default)")
    parser.add_argument("--host", type=str, default="0.0.0.0",
                        help="Interface to bind on (default: 0.0.0.0)")
    parser.add_argument("--ldap-host", type=str, default="localhost",
                        help="LDAP directory server host (default: localhost)")
    parser.add_argument("--ldap-port", type=int, default=9389,
                        help="LDAP directory server port (default: 9389)")
    args = parser.parse_args()

    service_type = args.service_type
    bind_host    = args.host
    port         = args.port or DEFAULT_PORTS[service_type]
    ldap_host    = args.ldap_host
    ldap_port    = args.ldap_port

    # -----------------------------------------------------------------------
    # Step 1: Register with the LDAP directory server
    # -----------------------------------------------------------------------
    # Determine the advertised host (the address subscribers will connect to).
    # When binding on 0.0.0.0 we advertise the machine's primary hostname so
    # remote subscribers can reach us.
    advertise_host = socket.gethostname() if bind_host == "0.0.0.0" else bind_host

    print("=" * 60)
    print(f"  Publisher: {service_type}")
    print("=" * 60)
    print(f"[LDAP] Connecting to directory server at {ldap_host}:{ldap_port}...")

    try:
        ldap_client.ldap_register(
            service_name = service_type,
            host         = advertise_host,
            port         = port,
            description  = SERVICE_DESCRIPTIONS[service_type],
            ldap_host    = ldap_host,
            ldap_port    = ldap_port,
        )
        print(f"[LDAP] Registered  cn={service_type},ou=services,dc=pubsub,dc=com")
        print(f"[LDAP]   host={advertise_host}  port={port}")
    except Exception as e:
        print(f"[LDAP] ERROR: Could not register service – {e}")
        print("[LDAP] Is ldap_server.py running? Start it first.")
        sys.exit(1)

    # -----------------------------------------------------------------------
    # Step 2: Bind the ZeroMQ PUB socket
    # -----------------------------------------------------------------------
    context = zmq.Context()
    socket_zmq = context.socket(zmq.PUB)
    address = f"tcp://{bind_host}:{port}"
    socket_zmq.bind(address)

    print(f"\n[ZMQ]  Publisher bound to {address}")
    print(f"[ZMQ]  Publishing messages every 3 seconds...")
    print("-" * 60)

    # Brief pause so subscribers can connect
    time.sleep(1)

    message_count = 0
    try:
        while True:
            time.sleep(3)
            content   = GENERATORS[service_type]()
            timestamp = time.strftime("%H:%M:%S")
            message   = f"{service_type} [{timestamp}] {content}"
            socket_zmq.send(message.encode("utf-8"))
            message_count += 1
            print(f"[{message_count:4d}] Published: {message}")

    except KeyboardInterrupt:
        print(f"\n{service_type} Publisher shutting down...")
        socket_zmq.close()
        context.term()


if __name__ == "__main__":
    main()
