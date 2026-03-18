import socket
import threading

# ── Configuration ────────────────────────────────────────────────────────────
REPLICA_HOST = "0.0.0.0"
REPLICA_PORT = 9001

BUFFER = 4096
# ─────────────────────────────────────────────────────────────────────────────

registry: dict[str, tuple[str, str]] = {}   # SERVICE → (host, port)
registry_lock = threading.Lock()


def handle_client(conn: socket.socket, addr: tuple) -> None:
    """Handle one incoming connection (from main_server or consumer)."""
    print(f"[CONN] Connection from {addr[0]}:{addr[1]}")
    try:
        data = conn.recv(BUFFER).decode().strip()
        if not data:
            return

        parts = data.split()
        command = parts[0].upper() if parts else ""

        # ── SYNC <SERVICE> <host> <port>  (from main server) ─────────────
        if command == "SYNC" and len(parts) == 4:
            _, service, host, port = parts
            service = service.upper()
            with registry_lock:
                registry[service] = (host, port)
            print(f"[SYNC]   Stored  {service} → {host}:{port}")
            conn.sendall(b"ACK\n")

        # ── LOOKUP <SERVICE>  (from consumer, when main is down) ──────────
        elif command == "LOOKUP" and len(parts) == 2:
            service = parts[1].upper()
            with registry_lock:
                entry = registry.get(service)
            if entry:
                host, port = entry
                reply = f"FOUND {host} {port}\n"
                print(f"[LOOKUP] {service} → {host}:{port}  (served as backup)")
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
    print("  REPLICA (Backup) Service Registry Server")
    print(f"  Listening on {REPLICA_HOST}:{REPLICA_PORT}")
    print("  (Will serve consumers if main server is down)")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((REPLICA_HOST, REPLICA_PORT))
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
        print("\n[INFO] Replica server shutting down.")
    finally:
        server.close()


if __name__ == "__main__":
    main()
