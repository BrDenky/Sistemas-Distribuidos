import socket
import json

# Default LDAP server location – override via environment or arguments
LDAP_HOST = "localhost"
LDAP_PORT = 9389


def _send_request(request: dict,
                  ldap_host: str = LDAP_HOST,
                  ldap_port: int = LDAP_PORT) -> dict:
    """Open a short-lived TCP connection, send *request*, return the response."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5)
        s.connect((ldap_host, ldap_port))
        s.sendall((json.dumps(request) + "\n").encode("utf-8"))

        # Read until newline
        data = b""
        while not data.endswith(b"\n"):
            chunk = s.recv(4096)
            if not chunk:
                break
            data += chunk

    return json.loads(data.decode("utf-8"))


# ---------------------------------------------------------------------------
def ldap_register(service_name: str,
                  host: str,
                  port: int,
                  description: str = "",
                  ldap_host: str = LDAP_HOST,
                  ldap_port: int = LDAP_PORT) -> None:
    """
    Register a service entry in the LDAP directory (ADD operation).

    Corresponds to adding this LDAP entry:
        dn: cn=<SERVICE>,ou=services,dc=pubsub,dc=com
        cn: <SERVICE>
        host: <host>
        port: <port>
        description: <description>

    Raises RuntimeError if the server returns an error.
    """
    request = {
        "operation":   "ADD",
        "cn":          service_name.upper(),
        "host":        host,
        "port":        port,
        "description": description or f"{service_name} publisher service",
    }
    response = _send_request(request, ldap_host, ldap_port)
    if response.get("status") != "ok":
        raise RuntimeError(f"LDAP ADD failed: {response.get('message')}")


def ldap_lookup(service_name: str,
                ldap_host: str = LDAP_HOST,
                ldap_port: int = LDAP_PORT) -> tuple:
    """
    Look up a service in the LDAP directory (SEARCH operation).

    Searches for:
        cn=<SERVICE>,ou=services,dc=pubsub,dc=com

    Returns:
        (host: str, port: int)

    Raises RuntimeError if the service is not found or the server errors.
    """
    request = {
        "operation": "SEARCH",
        "cn":        service_name.upper(),
    }
    response = _send_request(request, ldap_host, ldap_port)
    if response.get("status") != "ok":
        raise RuntimeError(
            f"LDAP SEARCH failed for '{service_name}': {response.get('message')}"
        )
    return response["host"], int(response["port"])
