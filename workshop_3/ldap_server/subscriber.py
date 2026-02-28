import zmq
import sys
import argparse
import ldap_client


# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="ZeroMQ Subscriber with LDAP-based service discovery",
        epilog="Example: python subscriber.py WEATHER NEWS"
    )
    parser.add_argument("services",
                        nargs="+",
                        type=str.upper,
                        metavar="SERVICE",
                        help="One or more services to subscribe to "
                             "(WEATHER, NEWS, SPORTS, FINANCE)")
    parser.add_argument("--ldap-host", type=str, default="localhost",
                        help="LDAP directory server host (default: localhost)")
    parser.add_argument("--ldap-port", type=int, default=9389,
                        help="LDAP directory server port (default: 9389)")
    args = parser.parse_args()

    services  = args.services
    ldap_host = args.ldap_host
    ldap_port = args.ldap_port

    print("=" * 60)
    print(f"  Subscriber – services: {', '.join(services)}")
    print("=" * 60)

    # -----------------------------------------------------------------------
    # Step 1: Query the LDAP directory to discover each service's address
    # -----------------------------------------------------------------------
    print(f"[LDAP] Querying directory server at {ldap_host}:{ldap_port}...")

    discovered = {}   # service -> (host, port)
    for service in services:
        try:
            host, port = ldap_client.ldap_lookup(
                service_name = service,
                ldap_host    = ldap_host,
                ldap_port    = ldap_port,
            )
            discovered[service] = (host, port)
            print(f"[LDAP] Discovered  cn={service},ou=services,dc=pubsub,dc=com")
            print(f"[LDAP]   → host={host}  port={port}")
        except RuntimeError as e:
            print(f"[LDAP] ERROR for '{service}': {e}")
            print(f"[LDAP] Make sure the '{service}' publisher is running and registered.")
            sys.exit(1)
        except Exception as e:
            print(f"[LDAP] Cannot reach directory server – {e}")
            print("[LDAP] Is ldap_server.py running?")
            sys.exit(1)

    # -----------------------------------------------------------------------
    # Step 2: Connect ZeroMQ SUB socket to all discovered addresses
    # -----------------------------------------------------------------------
    context    = zmq.Context()
    socket_zmq = context.socket(zmq.SUB)

    print()
    for service, (host, port) in discovered.items():
        address = f"tcp://{host}:{port}"
        socket_zmq.connect(address)
        socket_zmq.setsockopt_string(zmq.SUBSCRIBE, service)
        print(f"[ZMQ]  Connected to {service} at {address}")

    print("-" * 60)
    print("Receiving messages (Press Ctrl+C to stop)...")
    print("-" * 60)

    message_count = 0
    try:
        while True:
            message = socket_zmq.recv().decode("utf-8")
            message_count += 1
            print(f"[{message_count:4d}] {message}")

    except KeyboardInterrupt:
        print(f"\nSubscriber shutting down. Total messages received: {message_count}")
        socket_zmq.close()
        context.term()


if __name__ == "__main__":
    main()
