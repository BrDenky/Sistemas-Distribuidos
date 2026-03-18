import zmq
import sys
import socket as stdlib_socket

# ── Registry server addresses (known to consumer) ───────────────────────────
MAIN_HOST    = "127.0.0.1"
MAIN_PORT    = 9000

REPLICA_HOST = "127.0.0.1"
REPLICA_PORT = 9001

LOOKUP_TIMEOUT = 2      # seconds to wait for main server reply
BUFFER         = 1024
# ─────────────────────────────────────────────────────────────────────────────


def lookup_service(service: str) -> tuple[str, int] | None:
    """
    Try main server first. On failure, fall back to replica.
    Returns (host, port) or None if neither server knows the service.
    """
    servers = [
        ("MAIN",    MAIN_HOST,    MAIN_PORT),
        ("REPLICA", REPLICA_HOST, REPLICA_PORT),
    ]

    for label, host, port in servers:
        try:
            print(f"[LOOKUP] Querying {label} server ({host}:{port}) …")
            with stdlib_socket.create_connection((host, port),
                                                 timeout=LOOKUP_TIMEOUT) as s:
                msg = f"LOOKUP {service}\n"
                s.sendall(msg.encode())
                reply = s.recv(BUFFER).decode().strip()

            if reply.startswith("FOUND"):
                _, pub_host, pub_port = reply.split()
                print(f"[LOOKUP] ✓ {service} found via {label}: "
                      f"{pub_host}:{pub_port}")
                return pub_host, int(pub_port)

            elif reply == "NOT_FOUND":
                print(f"[LOOKUP] {label}: service '{service}' not registered.")
                return None

        except (ConnectionRefusedError, TimeoutError, OSError) as exc:
            print(f"[LOOKUP] {label} server unreachable: {exc}")
            if label == "MAIN":
                print("[LOOKUP] ↳ Falling back to REPLICA server…")

    print(f"[LOOKUP] ✗ Could not resolve '{service}' from any server.")
    return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python consumer.py <SERVICE> [SERVICE2] …")
        print("Services: WEATHER  NEWS  SPORTS  FINANCE")
        sys.exit(1)

    requested = [s.upper() for s in sys.argv[1:]]

    print("  Consumer – Service Discovery with Replica Fallback")
    print(f"  Main server   : {MAIN_HOST}:{MAIN_PORT}")
    print(f"  Replica server: {REPLICA_HOST}:{REPLICA_PORT}")
    print(f"  Requested     : {', '.join(requested)}")

    context = zmq.Context()
    sub = context.socket(zmq.SUB)

    connected = []
    for service in requested:
        result = lookup_service(service)
        if result is None:
            print(f"[WARN] Skipping '{service}' – not found on any server.\n")
            continue
        pub_host, pub_port = result
        address = f"tcp://{pub_host}:{pub_port}"
        sub.connect(address)
        sub.setsockopt_string(zmq.SUBSCRIBE, service)
        print(f"[ZMQ]  Subscribed to {service} at {address}\n")
        connected.append(service)

    if not connected:
        print("[ERROR] No services could be resolved. Exiting.")
        sub.close()
        context.term()
        sys.exit(1)

    print(f"Receiving messages for: {', '.join(connected)}")
    print("Press Ctrl+C to stop.")

    count = 0
    try:
        while True:
            message = sub.recv().decode("utf-8")
            count += 1
            print(f"[{count:>4}] {message}")
    except KeyboardInterrupt:
        print(f"\n[INFO] Consumer shutting down. Total received: {count}")
    finally:
        sub.close()
        context.term()


if __name__ == "__main__":
    main()
