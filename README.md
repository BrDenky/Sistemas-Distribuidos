# Network Socket Programming Laboratory
## Complete Workshop - All Activities (1-7)

This repository contains complete implementations for a network socket programming laboratory, including Python, C++, and JavaScript versions with multithreading support.

---

## 📁 Project Structure

```
Sistemas/
├── Python Files
│   ├── server-socket.py              # Original single-threaded server
│   ├── server-multithreaded.py       # Multithreaded server (Activity 3)
│   ├── client-socket.py              # Original interactive client
│   ├── client-remote.py              # Client with remote host support (Activity 2)
│   └── client-random.py              # Random message client (Activity 4)
│
├── C++ Files (Activity 6)
│   ├── server-socket.cpp             # C++ multithreaded server
│   ├── client-socket.cpp             # C++ interactive client
│   └── client-random.cpp             # C++ random message client
│
├── JavaScript Files (Activity 7)
│   ├── client-socket.js              # Node.js interactive client
│   └── client-random.js              # Node.js random message client
│
└── Documentation
    ├── README.md                     # This file
    ├── compile-instructions.md       # C++ compilation guide
    └── testing-guide.md              # Complete testing procedures
```

---

## 🎯 Workshop Activities Overview

### ✅ Activity 1: Test on Same Machine
Test Python server and client on localhost to verify basic functionality.

### ✅ Activity 2: Test on Different Hosts
Test client and server running on different machines across the network.

### ✅ Activity 3: Multithreading Support
Enhanced server to handle multiple concurrent clients using Python's threading module.

### ✅ Activity 4: Random Message Client
Client that sends a random number of messages with random content and auto-terminates.

### ✅ Activity 5: Test Random Client
Test random client on different hosts with concurrent connections.

### ✅ Activity 6: C++ Implementation
Complete C++ versions of server and client using Winsock API.

### ✅ Activity 7: Cross-Language Testing
Test clients and servers in different language combinations.

---

## 🚀 Quick Start Guide

### Python Programs

**1. Start the multithreaded server:**
```bash
python server-multithreaded.py
```

**2. Run interactive client (localhost):**
```bash
python client-socket.py
```

**3. Run interactive client (remote host):**
```bash
python client-remote.py 192.168.1.100
```

**4. Run random message client:**
```bash
python client-random.py
# Or with remote host:
python client-random.py 192.168.1.100
```

### C++ Programs

**1. Compile the programs (see [compile-instructions.md](file:///c:/Users/ASUS/Desktop/Sistemas/compile-instructions.md)):**
```bash
g++ -std=c++11 server-socket.cpp -o server-socket.exe -lws2_32
g++ -std=c++11 client-socket.cpp -o client-socket.exe -lws2_32
g++ -std=c++11 client-random.cpp -o client-random.exe -lws2_32
```

**2. Run the programs:**
```bash
# Server
./server-socket.exe

# Client
./client-socket.exe
# Or with remote host:
./client-socket.exe 192.168.1.100

# Random client
./client-random.exe
```

### JavaScript Programs

**1. Install Node.js** (if not already installed)
- Download from: https://nodejs.org/

**2. Run the programs:**
```bash
# Interactive client
node client-socket.js
# Or with remote host:
node client-socket.js 192.168.1.100

# Random client
node client-random.js
# Or with remote host:
node client-random.js 192.168.1.100
```

---

## 🧪 Testing Procedures

### Activity 1: Local Testing
1. Open two terminals
2. Terminal 1: `python server-multithreaded.py`
3. Terminal 2: `python client-socket.py`
4. Send messages and verify responses

### Activity 2: Remote Testing (Manual)
1. On Server Machine:
   - Find IP address: `ipconfig` (Windows) or `ifconfig` (Linux/Mac)
   - Run: `python server-multithreaded.py`
   - Configure firewall to allow port 12000
2. On Client Machine:
   - Run: `python client-remote.py <SERVER_IP>`
   - Verify connection and message exchange

### Activity 3: Concurrent Clients
1. Start server: `python server-multithreaded.py`
2. Open 3+ terminals and run clients simultaneously:
   - Terminal 2: `python client-socket.py`
   - Terminal 3: `python client-socket.py`
   - Terminal 4: `python client-socket.py`
3. Send messages from all clients and verify server handles them concurrently

### Activity 4: Random Message Client
1. Start server: `python server-multithreaded.py`
2. Run: `python client-random.py`
3. Observe random number of messages being sent
4. Verify client auto-terminates

### Activity 5: Concurrent Random Clients
1. Start server: `python server-multithreaded.py`
2. Run multiple random clients simultaneously:
   - `python client-random.py`
   - `python client-random.py`
   - `python client-random.py`
3. Verify all clients complete successfully

### Activity 6: C++ Testing
1. Compile all C++ programs
2. Test C++ server with C++ client
3. Verify functionality matches Python version

### Activity 7: Cross-Language Testing Matrix

| Server | Client | Status |
|--------|--------|--------|
| Python | C++ | ✅ Compatible |
| Python | JavaScript | ✅ Compatible |
| C++ | Python | ✅ Compatible |
| C++ | JavaScript | ✅ Compatible |

**Test each combination:**
```bash
# Example: Python server + C++ client
Terminal 1: python server-multithreaded.py
Terminal 2: ./client-socket.exe

# Example: C++ server + JavaScript client
Terminal 1: ./server-socket.exe
Terminal 2: node client-socket.js
```

---

## 🔧 Technical Details

### Protocol
- **Transport**: TCP (SOCK_STREAM)
- **Port**: 12000
- **Encoding**: UTF-8 text
- **Functionality**: Converts lowercase messages to uppercase

### Server Features
- Multithreaded connection handling
- Supports unlimited concurrent clients
- 3-second processing delay (simulates work)
- Connection logging with client IP and port

### Client Features
- Command-line server IP specification
- Interactive mode (original client)
- Random message mode (sends 1-10 random messages)
- Error handling and connection retry logic

---

## 🛡️ Firewall Configuration

### Windows Firewall
```powershell
# Allow inbound connections on port 12000
netsh advfirewall firewall add rule name="Socket Server" dir=in action=allow protocol=TCP localport=12000
```

### Linux (ufw)
```bash
sudo ufw allow 12000/tcp
```

---

## 📊 Expected Output Examples

### Server Output
```
The multithreaded server is ready to receive on port 12000
[NEW CONNECTION] Client connected from: ('127.0.0.1', 54321)
[127.0.0.1:54321] Received: hello world
[127.0.0.1:54321] Response sent
[DISCONNECTED] 127.0.0.1:54321
[ACTIVE CONNECTIONS] 0
```

### Client Output (Interactive)
```
Connecting to server at localhost:12000
Input lowercase sentence: hello world
From Server: HELLO WORLD
Other message: (Y/N) N
```

### Client Output (Random)
```
Client will send 5 random messages to localhost:12000

[Message 1/5] Sending: abc def ghi
[Message 1/5] From Server: ABC DEF GHI

[Message 2/5] Sending: xyz test message
[Message 2/5] From Server: XYZ TEST MESSAGE
...
✓ Successfully sent all 5 messages. Client terminating.
```

---

## 🐛 Troubleshooting

### "Connection Refused"
- Ensure server is running before starting client
- Verify correct IP address and port
- Check firewall settings

### "Address Already in Use"
- Another process is using port 12000
- Kill the existing process or change the port

### C++ Compilation Errors
- See [compile-instructions.md](file:///c:/Users/ASUS/Desktop/Sistemas/compile-instructions.md)
- Ensure Winsock library is linked (`-lws2_32`)

### JavaScript "Cannot find module"
- Ensure Node.js is installed
- The `net` and `readline` modules are built-in, no npm install needed

---

## 📝 Notes

- All implementations use the same protocol and are interoperable
- Server must be started before clients
- Port 12000 is used by default in all implementations
- For remote testing, ensure both machines are on the same network or have proper routing configured
- The multithreaded server can handle hundreds of concurrent connections

---

## 👨‍💻 Author
Workshop completed for Semester I 2026 - Prof. Francisco Hidrobo

## 📅 Date
February 4, 2026
