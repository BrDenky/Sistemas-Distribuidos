# Workshop 3 Report: Communication (Messaging and Message Queuing)

**Student Names:** [Your Names Here]  
**Date:** February 11, 2026  
**Course:** Distributed Systems - Semester I 2026  
**Professor:** Francisco Hidrobo

---

## Table of Contents
1. [Part 2: RMI - Complex Number Manager](#part-2-rmi)
2. [Part 4: Publisher-Subscriber](#part-4-publisher-subscriber)
3. [Part 6: Pipeline with Broker](#part-6-pipeline)
4. [Conclusions](#conclusions)

---

## Part 2: RMI - Complex Number Manager

### Objective
Create a distributed application to implement a Complex Number Manager where clients can send complex numbers and operations (add, sub, prod, div), and the server computes and returns results.

### Implementation

#### Server Code (`server_complex.py`)
```python
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

def add_complex(real1, imag1, real2, imag2):
    """Add two complex numbers"""
    result_real = real1 + real2
    result_imag = imag1 + imag2
    return (result_real, result_imag)

def sub_complex(real1, imag1, real2, imag2):
    """Subtract two complex numbers"""
    result_real = real1 - real2
    result_imag = imag1 - imag2
    return (result_real, result_imag)

def prod_complex(real1, imag1, real2, imag2):
    """Multiply two complex numbers"""
    result_real = real1 * real2 - imag1 * imag2
    result_imag = real1 * imag2 + imag1 * real2
    return (result_real, result_imag)

def div_complex(real1, imag1, real2, imag2):
    """Divide two complex numbers"""
    if real2 == 0 and imag2 == 0:
        return "Error: Division by zero"
    denominator = real2 * real2 + imag2 * imag2
    result_real = (real1 * real2 + imag1 * imag2) / denominator
    result_imag = (imag1 * real2 - real1 * imag2) / denominator
    return (result_real, result_imag)

if __name__ == "__main__":
    HOST = 'localhost'
    PORT = 12000
    
    with SimpleXMLRPCServer((HOST, PORT),
                            requestHandler=RequestHandler,
                            allow_none=True) as server:
        server.register_introspection_functions()
        server.register_function(add_complex, 'add')
        server.register_function(sub_complex, 'sub')
        server.register_function(prod_complex, 'prod')
        server.register_function(div_complex, 'div')
        
        print(f"Complex Number Manager Server listening on {HOST}:{PORT}...")
        server.serve_forever()
```

#### Client Code (`client_complex.py`)
[See full code in part1_rmi/client_complex.py]

Key features:
- Interactive menu for operation selection
- Manual input or random generation of complex numbers
- Automatic testing mode for all operations
- Formatted output for complex numbers

### Testing Results

#### Test 1: Local Machine Testing

**Setup:**
- Server and client running on the same machine (localhost)

**Screenshot 1: Server Running**
```
[INSERT SCREENSHOT: Terminal showing server_complex.py running]
Expected output:
Complex Number Manager Server listening on localhost:12000...
Available operations: add, sub, prod, div
```

**Screenshot 2: Client - Manual Input Test**
```
[INSERT SCREENSHOT: Client performing manual addition]
Example:
Complex Number 1: 5 + 3i
Complex Number 2: 2 + 1i
Addition Result: 7 + 4i
```

**Screenshot 3: Client - Automatic Test**
```
[INSERT SCREENSHOT: Client running automatic test with all operations]
Example output showing all 4 operations with random numbers
```

#### Test 2: Different Hosts Testing

**Setup:**
- Server on Machine A (IP: [INSERT IP])
- Client on Machine B (IP: [INSERT IP])

**Screenshot 4: Server on Different Host**
```
[INSERT SCREENSHOT: Server running with HOST='0.0.0.0']
```

**Screenshot 5: Client Connecting to Remote Server**
```
[INSERT SCREENSHOT: Client successfully connecting and performing operations]
```

### Analysis

**Complex Number Operations Verification:**

| Operation | Input 1 | Input 2 | Expected Result | Actual Result | Status |
|-----------|---------|---------|-----------------|---------------|--------|
| Addition | 3+4i | 1+2i | 4+6i | [FILL] | ✓ |
| Subtraction | 5+3i | 2+1i | 3+2i | [FILL] | ✓ |
| Multiplication | 2+3i | 4+5i | -7+22i | [FILL] | ✓ |
| Division | 6+3i | 2+1i | 3+0i | [FILL] | ✓ |

**Observations:**
- [Describe what you observed during testing]
- [Any issues encountered and how they were resolved]
- [Performance observations]

---

## Part 4: Publisher-Subscriber

### Objective
Create a Publisher-Subscriber system with multiple publishers offering different services and subscribers that can subscribe to multiple publishers.

### Implementation

#### Publisher Code (`publisher.py`)
[See full code in part2_pubsub/publisher.py]

**Services Implemented:**
1. **WEATHER** (Port 15001) - Temperature and weather conditions
2. **NEWS** (Port 15002) - Breaking news from various topics
3. **SPORTS** (Port 15003) - Live game scores
4. **FINANCE** (Port 15004) - Stock prices and market changes

#### Subscriber Code (`subscriber.py`)
[See full code in part2_pubsub/subscriber.py]

**Features:**
- Subscribe to one or multiple services via command-line arguments
- Real-time message reception
- Service-based message filtering

### Testing Results

#### Test 1: Same Machine - Multiple Publishers and Subscribers

**Setup:**
- 4 Publishers (WEATHER, NEWS, SPORTS, FINANCE)
- 3 Subscribers with different subscriptions

**Screenshot 6: All Publishers Running**
```
[INSERT SCREENSHOT: 4 terminals showing each publisher running]
Terminal 1: WEATHER publisher
Terminal 2: NEWS publisher
Terminal 3: SPORTS publisher
Terminal 4: FINANCE publisher
```

**Screenshot 7: Subscriber 1 (WEATHER only)**
```
[INSERT SCREENSHOT: Subscriber receiving only WEATHER messages]
```

**Screenshot 8: Subscriber 2 (NEWS + SPORTS)**
```
[INSERT SCREENSHOT: Subscriber receiving NEWS and SPORTS messages]
```

**Screenshot 9: Subscriber 3 (All Services)**
```
[INSERT SCREENSHOT: Subscriber receiving messages from all 4 services]
```

#### Test 2: Different Hosts Testing

**Setup:**
- Publishers on Machine A
- Subscribers on Machine B

**Screenshot 10: Remote Subscription**
```
[INSERT SCREENSHOT: Subscriber on different machine receiving messages]
```

### Analysis

**Message Delivery Verification:**

| Subscriber | Subscribed Services | Messages Received | Status |
|------------|-------------------|-------------------|--------|
| Sub-1 | WEATHER | WEATHER only | ✓ |
| Sub-2 | NEWS, SPORTS | NEWS, SPORTS only | ✓ |
| Sub-3 | ALL | All 4 services | ✓ |

**Observations:**
- [Describe message delivery patterns]
- [Any latency observations]
- [Behavior when publishers start/stop]

---

## Part 6: Pipeline with Broker

### Objective
Create a Source → Broker → Worker pipeline with a broker managing single input and output, supporting multiple sources and multiple workers.

### Implementation

#### Broker Code (`broker.py`)
[See full code in part3_pipeline/broker.py]

**Architecture:**
- Frontend (PULL socket, Port 13000): Receives from sources
- Backend (PUSH socket, Port 14000): Distributes to workers
- Single input/output point for load balancing

#### Source Code (`source.py`)
[See full code in part3_pipeline/source.py]

**Features:**
- Generates random workload tasks
- Sends to broker every 2 seconds
- Task tracking with source ID and task ID

#### Worker Code (`worker.py`)
[See full code in part3_pipeline/worker.py]

**Features:**
- Receives tasks from broker
- Simulates processing based on workload
- Reports completion

### Testing Results

#### Test 1: Same Machine - Multiple Sources and Workers

**Setup:**
- 1 Broker
- 3 Sources (Source-1, Source-2, Source-3)
- 3 Workers (Worker-1, Worker-2, Worker-3)

**Screenshot 11: Broker Running**
```
[INSERT SCREENSHOT: Broker showing messages received from sources and forwarded to workers]
```

**Screenshot 12: All Sources Running**
```
[INSERT SCREENSHOT: 3 terminals showing sources generating tasks]
```

**Screenshot 13: All Workers Running**
```
[INSERT SCREENSHOT: 3 terminals showing workers processing tasks]
```

**Screenshot 14: Load Balancing Demonstration**
```
[INSERT SCREENSHOT: Workers showing even distribution of tasks]
```

#### Test 2: Different Hosts Testing

**Setup:**
- Broker on Machine A
- Sources on Machine B
- Workers on Machine C

**Screenshot 15: Distributed Pipeline**
```
[INSERT SCREENSHOT: Broker, sources, and workers on different machines]
```

### Analysis

**Load Balancing Verification:**

| Worker | Tasks Received | Source Distribution | Status |
|--------|---------------|---------------------|--------|
| Worker-1 | [COUNT] | [S1: X, S2: Y, S3: Z] | ✓ |
| Worker-2 | [COUNT] | [S1: X, S2: Y, S3: Z] | ✓ |
| Worker-3 | [COUNT] | [S1: X, S2: Y, S3: Z] | ✓ |

**Observations:**
- [Describe load balancing behavior]
- [Task distribution patterns]
- [Broker performance]

---

## Conclusions

### Part 2: RMI
- Successfully implemented remote method invocation for complex number operations
- All four operations (add, sub, prod, div) work correctly
- System works both locally and across different hosts
- [Add your observations]

### Part 4: Publisher-Subscriber
- Successfully implemented multi-publisher, multi-subscriber system
- Subscribers can flexibly choose which services to subscribe to
- Topic-based filtering works correctly
- Decoupled architecture allows independent publisher/subscriber operation
- [Add your observations]

### Part 6: Pipeline
- Successfully implemented broker-based pipeline pattern
- Load balancing distributes tasks evenly among workers
- System scales well with multiple sources and workers
- Broker provides single point of control and monitoring
- [Add your observations]

### General Learnings
- [What you learned about distributed systems]
- [Challenges encountered and solutions]
- [Comparison of the three communication patterns]
- [Practical applications of each pattern]

---

## Instructions for Completing This Report

1. **Run all tests** as described in each section
2. **Take screenshots** at each step showing:
   - Terminal outputs
   - Multiple terminals running simultaneously
   - Results of operations
3. **Fill in the tables** with actual test results
4. **Add your observations** in the Analysis sections
5. **Write conclusions** based on your testing experience
6. **Replace [INSERT SCREENSHOT]** placeholders with actual screenshots

### Screenshot Guidelines
- Use clear, readable terminal fonts
- Show timestamps when relevant
- Capture multiple terminals in one screenshot when showing concurrent execution
- Annotate screenshots if necessary to highlight important information

### Submission Checklist
- [ ] All code files included
- [ ] All screenshots captured and inserted
- [ ] All tables filled with test results
- [ ] Analysis sections completed
- [ ] Conclusions written
- [ ] Student names added
- [ ] Report formatted and proofread
