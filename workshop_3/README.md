# Workshop 3: Communication (Messaging and Message Queuing)
**Distributed Systems - Semester I 2026**

## Overview
This workshop implements three distributed communication patterns in Python:
1. **RMI**: Remote Method Invocation for Complex Number operations
2. **Publisher-Subscriber**: Multi-service messaging system
3. **Pipeline**: Source → Broker → Worker with load balancing

## Project Structure
```
workshop_3/
├── part1_rmi/
│   ├── server_complex.py
│   ├── client_complex.py
│   └── README.md
├── part2_pubsub/
│   ├── publisher.py
│   ├── subscriber.py
│   └── README.md
├── part3_pipeline/
│   ├── broker.py
│   ├── source.py
│   ├── worker.py
│   └── README.md
└── README.md (this file)
```

## Requirements

### Python Version
- Python 3.7 or higher

### Dependencies
Install required libraries:
```bash
pip install pyzmq
```

**Note**: Part 1 (RMI) uses built-in `xmlrpc` library and requires no additional installation.

## Quick Start Guide

### Part 1: RMI - Complex Number Manager

**Start Server:**
```bash
cd part1_rmi
python server_complex.py
```

**Start Client (new terminal):**
```bash
python client_complex.py
```

**Features:**
- Addition, subtraction, multiplication, division of complex numbers
- Manual input or random generation
- Automatic testing mode

See [part1_rmi/README.md](part1_rmi/README.md) for detailed instructions.

---

### Part 2: Publisher-Subscriber

**Start Publishers (separate terminals):**
```bash
cd part2_pubsub
python publisher.py WEATHER
python publisher.py NEWS
python publisher.py SPORTS
python publisher.py FINANCE
```

**Start Subscribers (separate terminals):**
```bash
# Subscribe to single service
python subscriber.py WEATHER

# Subscribe to multiple services
python subscriber.py NEWS SPORTS

# Subscribe to all services
python subscriber.py WEATHER NEWS SPORTS FINANCE
```

**Available Services:**
- WEATHER (Port 15001)
- NEWS (Port 15002)
- SPORTS (Port 15003)
- FINANCE (Port 15004)

See [part2_pubsub/README.md](part2_pubsub/README.md) for detailed instructions.

---

### Part 3: Pipeline with Broker

**Start Broker:**
```bash
cd part3_pipeline
python broker.py
```

**Start Workers (separate terminals):**
```bash
python worker.py 1
python worker.py 2
python worker.py 3
```

**Start Sources (separate terminals):**
```bash
python source.py 1
python source.py 2
python source.py 3
```

**Architecture:**
- Sources generate tasks → Broker receives and distributes → Workers process tasks
- Automatic load balancing
- Scalable design

See [part3_pipeline/README.md](part3_pipeline/README.md) for detailed instructions.

---

## Testing on Different Hosts

All three parts support distributed testing across different machines:

1. **Server/Publisher/Broker side**: Change `HOST` variable to `'0.0.0.0'` or specific IP
2. **Client/Subscriber/Worker side**: Change `HOST` variable to server's IP address
3. Ensure firewall allows connections on required ports

### Port Usage Summary
- **Part 1 (RMI)**: Port 12000
- **Part 2 (Pub-Sub)**: Ports 15001-15004
- **Part 3 (Pipeline)**: Ports 13000 (frontend), 14000 (backend)

## Implementation Highlights

### Part 1: RMI
- ✅ Complex number arithmetic (all 4 operations)
- ✅ Error handling (division by zero)
- ✅ Interactive client with menu
- ✅ Random number generation for testing
- ✅ Clean formatted output

### Part 2: Publisher-Subscriber
- ✅ Multiple publishers (4 different services)
- ✅ Multiple subscribers with flexible subscriptions
- ✅ Topic-based message filtering
- ✅ Decoupled architecture
- ✅ Real-time message delivery

### Part 3: Pipeline
- ✅ Broker pattern (single input/output)
- ✅ Multiple sources support
- ✅ Multiple workers support
- ✅ Automatic load balancing
- ✅ Task tracking and monitoring

## Troubleshooting

### Common Issues

**"Address already in use" error:**
- Wait a few seconds for the port to be released
- Or change the port number in both server and client

**"Connection refused" error:**
- Ensure server/broker is running first
- Check firewall settings
- Verify correct IP address and port

**ZeroMQ not found:**
```bash
pip install pyzmq
```

**No messages received in subscriber:**
- Ensure publisher is running
- Check that service names match exactly (case-sensitive)
- Verify port numbers are correct

## Author
Workshop completed for Distributed Systems course, Semester I 2026

## References
- Python XML-RPC Documentation: https://docs.python.org/3/library/xmlrpc.html
- ZeroMQ Guide: https://zguide.zeromq.org/
- ZeroMQ Python Bindings: https://pyzmq.readthedocs.io/
