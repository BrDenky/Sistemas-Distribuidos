# Part 3: Pipeline Communication with Broker

## Description
This implementation provides a Source → Broker → Worker pipeline pattern using ZeroMQ. The broker acts as an intermediary with a single input (from multiple sources) and single output (to multiple workers), enabling load balancing and decoupling.

## Files
- `broker.py` - Central broker that receives from sources and distributes to workers
- `source.py` - Task generator that sends work to broker
- `worker.py` - Task processor that receives work from broker

## Architecture

```
Source-1 ──┐
           │
Source-2 ──┼──> BROKER ──┬──> Worker-1
           │              │
Source-3 ──┘              ├──> Worker-2
                          │
                          └──> Worker-3
```

- **Frontend (PULL socket)**: Receives tasks from multiple sources (Port 13000)
- **Backend (PUSH socket)**: Distributes tasks to multiple workers (Port 14000)
- **Load Balancing**: ZeroMQ automatically distributes work evenly among workers

## Usage

### Local Testing (Same Machine)

1. **Start the broker first:**
```bash
python broker.py
```

2. **Start multiple workers (each in a separate terminal):**
```bash
python worker.py 1
python worker.py 2
python worker.py 3
```

3. **Start multiple sources (each in a separate terminal):**
```bash
python source.py 1
python source.py 2
python source.py 3
```

### Testing on Different Hosts

#### Broker Machine:
- No changes needed (already binds to all interfaces with `*`)
- Run: `python broker.py`
- Note the broker's IP address

#### Source Machines:
- Edit `source.py` line 18: Change `BROKER_HOST = 'localhost'` to broker's IP
- Run: `python source.py <source_id>`

#### Worker Machines:
- Edit `worker.py` line 18: Change `BROKER_HOST = 'localhost'` to broker's IP
- Run: `python worker.py <worker_id>`

## Example Output

**Broker:**
```
BROKER STARTED
Frontend (receiving from sources): tcp://*:13000
Backend (sending to workers): tcp://*:14000
Broker is running...
[1] [14:45:10] Received from Source-1: Task #1, Workload=45
    → Forwarded to workers
[2] [14:45:11] Received from Source-2: Task #1, Workload=78
    → Forwarded to workers
```

**Source-1:**
```
SOURCE-1 STARTED
Connected to broker at tcp://localhost:13000
Generating tasks every 2 seconds...
[14:45:10] Sent Task #1: Workload=45
[14:45:12] Sent Task #2: Workload=67
```

**Worker-1:**
```
WORKER-1 STARTED
Connected to broker at tcp://localhost:14000
Waiting for tasks...
[14:45:10] Task #1 received from Source-1 (Task #1): Workload=45
    Processing... (estimated 0.45s)
    ✓ Completed!
[14:45:13] Task #2 received from Source-3 (Task #2): Workload=89
    Processing... (estimated 0.89s)
    ✓ Completed!
```

## Features

- **Load Balancing**: Tasks automatically distributed evenly among workers
- **Scalability**: Add/remove sources and workers dynamically
- **Decoupling**: Sources and workers don't know about each other
- **Single Point of Control**: Broker manages all communication
- **Task Tracking**: Each task includes source ID, task ID, and workload
- **Simulated Processing**: Workers simulate work based on workload value

## Testing Scenarios

### Scenario 1: Single Source, Multiple Workers
```bash
# Terminal 1: Broker
python broker.py

# Terminal 2-4: Workers
python worker.py 1
python worker.py 2
python worker.py 3

# Terminal 5: Source
python source.py 1
```

### Scenario 2: Multiple Sources, Single Worker
```bash
# Terminal 1: Broker
python broker.py

# Terminal 2: Worker
python worker.py 1

# Terminal 3-5: Sources
python source.py 1
python source.py 2
python source.py 3
```

### Scenario 3: Multiple Sources, Multiple Workers (Full Pipeline)
```bash
# Terminal 1: Broker
python broker.py

# Terminal 2-4: Workers
python worker.py 1
python worker.py 2
python worker.py 3

# Terminal 5-7: Sources
python source.py 1
python source.py 2
python source.py 3
```

## Requirements
- Python 3.x
- ZeroMQ library: `pip install pyzmq`
