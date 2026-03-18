import zmq
import time
import sys
import random
import socket as stdlib_socket

# ── Registry server addresses ─────────────────────────────────────────────────
MAIN_HOST   = "127.0.0.1"
MAIN_PORT   = 9000

# ── Publisher ZMQ bind ────────────────────────────────────────────────────────
PUB_HOST    = "0.0.0.0"      # bind all interfaces
PUB_REPORT  = "127.0.0.1"   # address reported to the registry (what consumers connect to)

# Port map: one fixed port per service (easy to customise)
SERVICE_PORTS = {
    "WEATHER": 15001,
    "NEWS":    15002,
    "SPORTS":  15003,
    "FINANCE": 15004,
}

REGISTRY_TIMEOUT = 5        # seconds
BUFFER           = 1024
# ─────────────────────────────────────────────────────────────────────────────


def register_service(service: str, host: str, port: int) -> bool:
    """Register with main server. Returns True on success."""
    try:
        with stdlib_socket.create_connection((MAIN_HOST, MAIN_PORT),
                                             timeout=REGISTRY_TIMEOUT) as s:
            msg = f"REGISTER {service} {host} {port}\n"
            s.sendall(msg.encode())
            reply = s.recv(BUFFER).decode().strip()
            return reply == "OK"
    except Exception as exc:
        print(f"[REGISTRY] ERROR: could not reach main server – {exc}")
        return False


# ── Message generators ────────────────────────────────────────────────────────
def gen_weather():
    temp = random.randint(15, 35)
    cond = random.choice(["Sunny", "Cloudy", "Rainy", "Windy"])
    return f"Temperature: {temp}°C, Condition: {cond}"

def gen_news():
    topic = random.choice(["Politics", "Technology", "Science", "World"])
    return f"Breaking news in {topic}: Important event occurred"

def gen_sports():
    teams = ["Team A", "Team B", "Team C", "Team D"]
    t1, t2 = random.sample(teams, 2)
    s1, s2 = random.randint(0, 5), random.randint(0, 5)
    return f"{t1} {s1} – {s2} {t2}"

def gen_finance():
    stock  = random.choice(["AAPL", "GOOGL", "MSFT", "AMZN"])
    price  = random.uniform(100, 500)
    change = random.uniform(-5, 5)
    return f"{stock}: ${price:.2f} ({change:+.2f}%)"

GENERATORS = {
    "WEATHER": gen_weather,
    "NEWS":    gen_news,
    "SPORTS":  gen_sports,
    "FINANCE": gen_finance,
}
# ─────────────────────────────────────────────────────────────────────────────


def main():
    if len(sys.argv) < 2:
        print("Usage: python publisher.py <SERVICE>")
        print("Services:", ", ".join(SERVICE_PORTS))
        sys.exit(1)

    service = sys.argv[1].upper()
    if service not in SERVICE_PORTS:
        print(f"Unknown service '{service}'. Choose from: {', '.join(SERVICE_PORTS)}")
        sys.exit(1)

    port = SERVICE_PORTS[service]

    print(f"  Publisher – {service} service")
    print(f"  ZMQ PUB will bind on {PUB_HOST}:{port}")
    print(f"  Registering with main server at {MAIN_HOST}:{MAIN_PORT}")

    # Step 1: Register with main server
    if register_service(service, PUB_REPORT, port):
        print(f"[REGISTRY] ✓ Registered {service} at {PUB_REPORT}:{port}")
    else:
        print("[REGISTRY] ✗ Registration FAILED – aborting.")
        sys.exit(1)

    # Step 2: Bind ZMQ PUB socket
    context = zmq.Context()
    pub = context.socket(zmq.PUB)
    address = f"tcp://{PUB_HOST}:{port}"
    pub.bind(address)
    print(f"[ZMQ] Bound on {address}")
    print("Publishing every 3 s…  (Ctrl+C to stop)\n")

    time.sleep(1)   # give subscribers a moment to connect

    count = 0
    try:
        while True:
            time.sleep(3)
            content   = GENERATORS[service]()
            timestamp = time.strftime("%H:%M:%S")
            message   = f"{service} [{timestamp}] {content}"
            pub.send(message.encode("utf-8"))
            count += 1
            print(f"[{count:>4}] {message}")
    except KeyboardInterrupt:
        print(f"\n[INFO] {service} publisher shutting down.")
    finally:
        pub.close()
        context.term()


if __name__ == "__main__":
    main()
