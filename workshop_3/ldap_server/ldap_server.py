import socketserver
import json
import threading
import sys


sys.stdout.reconfigure(line_buffering=True)  # flush prints immediately on Windows

LDAP_PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9389
BASE_DN   = "dc=pubsub,dc=com"
OU        = "ou=services"

# In-memory directory  { cn: {dn, cn, host, port, description} }
_directory: dict = {}
_lock = threading.Lock()


def _build_dn(cn: str) -> str:
    return f"cn={cn},{OU},{BASE_DN}"


class LDAPHandler(socketserver.StreamRequestHandler):
    """Handle one client connection."""

    def handle(self):
        client_addr = self.client_address[0]
        try:
            raw = self.rfile.readline()
            if not raw:
                return
            request = json.loads(raw.decode("utf-8"))
            operation = request.get("operation", "").upper()

            if operation == "ADD":
                response = self._handle_add(request)
            elif operation == "SEARCH":
                response = self._handle_search(request)
            elif operation == "LIST":
                response = self._handle_list()
            else:
                response = {"status": "error", "message": f"Unknown operation: {operation}"}

        except json.JSONDecodeError as e:
            response = {"status": "error", "message": f"Invalid JSON: {e}"}
        except Exception as e:
            response = {"status": "error", "message": str(e)}

        self.wfile.write((json.dumps(response) + "\n").encode("utf-8"))

    # ------------------------------------------------------------------
    def _handle_add(self, req: dict) -> dict:
        cn   = req.get("cn", "").upper()
        host = req.get("host", "")
        port = req.get("port")
        desc = req.get("description", f"{cn} service")

        if not cn or not host or port is None:
            return {"status": "error", "message": "ADD requires cn, host, port"}

        dn = _build_dn(cn)
        entry = {"dn": dn, "cn": cn, "host": host, "port": int(port), "description": desc}

        with _lock:
            _directory[cn] = entry

        print(f"[ADD]    {dn}  host={host}  port={port}", flush=True)
        return {"status": "ok", "dn": dn, "message": f"Entry '{cn}' registered"}

    def _handle_search(self, req: dict) -> dict:
        cn = req.get("cn", "").upper()
        if not cn:
            return {"status": "error", "message": "SEARCH requires cn"}

        with _lock:
            entry = _directory.get(cn)

        if entry is None:
            base = f"{OU},{BASE_DN}"
            print(f"[SEARCH] cn={cn},{base}  → NOT FOUND", flush=True)
            return {"status": "error", "message": f"No entry found for cn={cn}"}

        print(f"[SEARCH] {entry['dn']}  → host={entry['host']}  port={entry['port']}", flush=True)
        return {
            "status": "ok",
            "dn":          entry["dn"],
            "cn":          entry["cn"],
            "host":        entry["host"],
            "port":        entry["port"],
            "description": entry["description"],
        }

    def _handle_list(self) -> dict:
        with _lock:
            entries = list(_directory.values())
        print(f"[LIST]   {len(entries)} entries", flush=True)
        return {"status": "ok", "entries": entries}


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads      = True


def main():
    host = "0.0.0.0"
    print("=" * 60)
    print("  LDAP Service Directory Server")
    print(f"  Base DN : {BASE_DN}")
    print(f"  Listening on {host}:{LDAP_PORT}")
    print("=" * 60)
    print("Waiting for publishers to register and subscribers to query...")
    print("Press Ctrl+C to stop.\n")

    with ThreadedTCPServer((host, LDAP_PORT), LDAPHandler) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nLDAP server shutting down.")


if __name__ == "__main__":
    main()
