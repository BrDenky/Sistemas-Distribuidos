# Part 2: Publisher-Subscriber with LDAP Service Discovery

## Description

This implementation extends the Publisher-Subscriber pattern (ZeroMQ) with an
**LDAP-inspired service directory server**. Instead of hardcoding IP addresses
and ports, publishers register their endpoint at startup and subscribers query
the directory to discover where to connect.

## Files

| File | Role |
|------|------|
| `ldap_server.py` | LDAP-like directory server (service registry) |
| `ldap_client.py` | Shared helper – register / lookup operations |
| `publisher.py`   | Registers with LDAP, then publishes messages via ZMQ PUB |
| `subscriber.py`  | Queries LDAP for each service, then subscribes via ZMQ SUB |

## Architecture

```
 Publisher                  LDAP Server (port 9389)             Subscriber
     │                              │                                │
     │─── ADD cn=WEATHER ──────────>│                                │
     │    host=<host>, port=15001   │                                │
     │                              │<── SEARCH cn=WEATHER ──────────│
     │                              │─── host=<host> port=15001 ────>│
     │                              │                                │
     │<════════ ZMQ PUB/SUB (tcp://host:15001) ═══════════════════>  │
```

### LDAP Data Model

```
dc=pubsub,dc=com
└── ou=services
    ├── cn=WEATHER   host=<host>  port=15001
    ├── cn=NEWS      host=<host>  port=15002
    ├── cn=SPORTS    host=<host>  port=15003
    └── cn=FINANCE   host=<host>  port=15004
```

## Available Services (default ports)

| Service | Default Port | Content |
|---------|-------------|---------|
| WEATHER | 15001 | Temperature & conditions |
| NEWS    | 15002 | Breaking news by topic |
| SPORTS  | 15003 | Live game scores |
| FINANCE | 15004 | Stock prices & changes |

## Usage

> **Important:** Always start the LDAP server **before** any publisher or subscriber.

### Step 1 – Start the LDAP directory server

```bash
python ldap_server.py
```

Output:
```
  LDAP Service Directory Server
  Base DN : dc=pubsub,dc=com
  Listening on 0.0.0.0:9389
```

### Step 2 – Start publishers (each in a separate terminal)

```bash
python publisher.py WEATHER
python publisher.py NEWS
python publisher.py SPORTS
python publisher.py FINANCE
```

Each publisher prints its LDAP registration then starts publishing:
```
[LDAP] Registered  cn=WEATHER,ou=services,dc=pubsub,dc=com
[LDAP]   host=MY-PC  port=15001
[ZMQ]  Publisher bound to tcp://0.0.0.0:15001
[   1] Published: WEATHER [14:30:15] Temperature: 25°C, Condition: Sunny
```

### Step 3 – Start subscriber(s)

```bash
# Subscribe to one service
python subscriber.py WEATHER

# Subscribe to multiple services
python subscriber.py NEWS SPORTS

# Subscribe to all
python subscriber.py WEATHER NEWS SPORTS FINANCE
```

The subscriber queries LDAP first, then connects:
```
[LDAP] Discovered  cn=WEATHER,ou=services,dc=pubsub,dc=com
[LDAP]   → host=MY-PC  port=15001
[LDAP] Discovered  cn=NEWS,ou=services,dc=pubsub,dc=com
[LDAP]   → host=MY-PC  port=15002
[ZMQ]  Connected to WEATHER at tcp://MY-PC:15001
[ZMQ]  Connected to NEWS at tcp://MY-PC:15002
Receiving messages...
[   1] WEATHER [14:30:15] Temperature: 25°C, Condition: Sunny
[   2] NEWS [14:30:16] Breaking news in Technology: Important event occurred
```

## Cross-Machine Testing

### On the publisher machine

Bind on all interfaces (default) and optionally specify a custom port:

```bash
python ldap_server.py          # Must be reachable by all machines!
python publisher.py WEATHER    # Registers with local LDAP and binds 0.0.0.0:15001
```

### On the subscriber machine

Point both the LDAP lookup and the ZMQ connection at the publisher's IP:

```bash
python subscriber.py WEATHER --ldap-host <PUBLISHER_IP>
```

The subscriber will automatically use whatever `host` the publisher registered
in LDAP — no manual IP editing required.

## Advanced Usage

### Custom ports

```bash
# Publisher on a non-default port
python publisher.py WEATHER --port 25001

# Subscriber discovers the port automatically via LDAP – no change needed!
python subscriber.py WEATHER --ldap-host <host>
```

### Custom LDAP server location

```bash
python publisher.py  WEATHER --ldap-host 192.168.1.10 --ldap-port 9389
python subscriber.py WEATHER --ldap-host 192.168.1.10 --ldap-port 9389
```

## Requirements

- Python 3.x
- `pyzmq` — `pip install pyzmq`
- No additional dependencies for the LDAP server (uses Python standard library only)
