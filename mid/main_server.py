import socket
import threading

# ── Configuration ────────────────────────────────────────────────────────────
MAIN_HOST    = "0.0.0.0"
MAIN_PORT    = 9000          # consumers and publishers connect here

REPLICA_HOST = "127.0.0.1"
REPLICA_PORT = 9001          # replica listens here

BUFFER      = 4096
SYNC_TIMEOUT = 2             # seconds to wait when syncing to replica
# ─────────────────────────────────────────────────────────────────────────────

registry: dict[str, tuple[str, str]] = {}   # SERVICE → (host, port)
registry_lock = threading.Lock()


def sync_to_replica(service: str, host: str, port: str) -> None:
    """Forward a registration to the replica server (best-effort)."""
    try:
        with socket.create_connection((REPLICA_HOST, REPLICA_PORT),
                                      timeout=SYNC_TIMEOUT) as s:
            msg = f"SYNC {service} {host} {port}\n"
            s.sendall(msg.encode())
            ack = s.recv(BUFFER).decode().strip()
            if ack == "ACK":
                print(f"[SYNC] Replica acknowledged  {service} → {host}:{port}")
            else:
                print(f"[SYNC] Unexpected reply from replica: {ack}")
    except Exception as exc:
        print(f"[SYNC] WARNING – could not reach replica: {exc}")


def handle_client(conn: socket.socket, addr: tuple) -> None:
    """Handle one connected client (publisher or consumer)."""
    print(f"[CONN] New connection from {addr[0]}:{addr[1]}")
    try:
        data = conn.recv(BUFFER).decode().strip()
        if not data:
            return

        parts = data.split()
        command = parts[0].upper() if parts else ""

        # ── REGISTER <SERVICE> <host> <port> ─────────────────────────────
        if command == "REGISTER" and len(parts) == 4:
            _, service, host, port = parts
            service = service.upper()
            with registry_lock:
                registry[service] = (host, port)
            print(f"[REGISTER] {service} → {host}:{port}")
            conn.sendall(b"OK\n")
            # Sync asynchronously so we don't block the publisher's reply
            threading.Thread(target=sync_to_replica,
                             args=(service, host, port),
                             daemon=True).start()

        # ── LOOKUP <SERVICE> ─────────────────────────────────────────────
        elif command == "LOOKUP" and len(parts) == 2:
            service = parts[1].upper()
            with registry_lock:
                entry = registry.get(service)
            if entry:
                host, port = entry
                reply = f"FOUND {host} {port}\n"
                print(f"[LOOKUP] {service} → {host}:{port}")
            else:
                reply = "NOT_FOUND\n"
                print(f"[LOOKUP] {service} – not found")
            conn.sendall(reply.encode())

        else:
            conn.sendall(b"ERROR unknown command\n")

    except Exception as exc:
        print(f"[ERROR] {exc}")
    finally:
        conn.close()


def main():
    print("  MAIN (Primary) Service Registry Server")
    print(f"  Listening on {MAIN_HOST}:{MAIN_PORT}")
    print(f"  Will sync registrations to replica at "
          f"{REPLICA_HOST}:{REPLICA_PORT}")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((MAIN_HOST, MAIN_PORT))
    server.listen(10)
    print("Waiting for connections…  (Ctrl+C to stop)\n")

    try:
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client,
                                      args=(conn, addr),
                                      daemon=True)
            thread.start()
    except KeyboardInterrupt:
        print("\n[INFO] Main server shutting down.")
    finally:
        server.close()


if __name__ == "__main__":
    main()
