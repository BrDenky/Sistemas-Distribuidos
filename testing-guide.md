# Testing Guide - Network Socket Laboratory

Complete testing procedures for all 7 workshop activities.

---

## 🧪 Activity 1: Test on Same Machine (Python)

### Objective
Verify basic functionality of Python server and client on localhost.

### Steps

1. **Open Terminal 1 - Start Server:**
   ```bash
   cd c:\Users\ASUS\Desktop\Sistemas
   python server-socket.py
   ```
   Expected output:
   ```
   The server is ready to receive
   ```

2. **Open Terminal 2 - Start Client:**
   ```bash
   cd c:\Users\ASUS\Desktop\Sistemas
   python client-socket.py
   ```

3. **Test Message Exchange:**
   ```
   Input lowercase sentence: hello world
   ```
   Expected response:
   ```
   From Server: HELLO WORLD
   ```

4. **Send Multiple Messages:**
   ```
   Other message: (Y/N) Y
   Input lowercase sentence: testing 123
   From Server: TESTING 123
   Other message: (Y/N) N
   ```

### ✅ Success Criteria
- Client connects successfully
- Messages are converted to uppercase
- Multiple messages can be sent
- Connection closes cleanly

---

## 🌐 Activity 2: Test on Different Hosts (Manual)

### Objective
Test client and server running on different machines.

### Prerequisites
- Two computers on the same network (or VMs)
- Firewall configured to allow port 12000

### Steps

**On Server Machine:**

1. **Find Server IP Address:**
   ```bash
   ipconfig
   ```
   Look for IPv4 Address (e.g., 192.168.1.100)

2. **Configure Firewall:**
   ```powershell
   netsh advfirewall firewall add rule name="Socket Server" dir=in action=allow protocol=TCP localport=12000
   ```

3. **Start Server:**
   ```bash
   python server-multithreaded.py
   ```

**On Client Machine:**

4. **Run Client with Server IP:**
   ```bash
   python client-remote.py 192.168.1.100
   ```
   (Replace 192.168.1.100 with actual server IP)

5. **Test Communication:**
   ```
   Input lowercase sentence: remote test
   From Server: REMOTE TEST
   ```

### ✅ Success Criteria
- Client connects to remote server
- Messages are exchanged across network
- No connection errors

### 🐛 Troubleshooting
- **Connection Refused**: Check firewall, verify IP address
- **Timeout**: Ensure both machines are on same network
- **No Response**: Verify server is running and listening

---

## 🔀 Activity 3: Multithreading Support

### Objective
Test server handling multiple concurrent clients.

### Steps

1. **Start Multithreaded Server:**
   ```bash
   python server-multithreaded.py
   ```
   Expected output:
   ```
   The multithreaded server is ready to receive on port 12000
   ```

2. **Open 3 Client Terminals Simultaneously:**

   **Terminal 2:**
   ```bash
   python client-socket.py
   ```

   **Terminal 3:**
   ```bash
   python client-socket.py
   ```

   **Terminal 4:**
   ```bash
   python client-socket.py
   ```

3. **Send Messages from All Clients at the Same Time:**
   - Client 1: `Input lowercase sentence: client one`
   - Client 2: `Input lowercase sentence: client two`
   - Client 3: `Input lowercase sentence: client three`

4. **Observe Server Output:**
   ```
   [NEW CONNECTION] Client connected from: ('127.0.0.1', 54321)
   [NEW CONNECTION] Client connected from: ('127.0.0.1', 54322)
   [NEW CONNECTION] Client connected from: ('127.0.0.1', 54323)
   [ACTIVE CONNECTIONS] 3
   [127.0.0.1:54321] Received: client one
   [127.0.0.1:54322] Received: client two
   [127.0.0.1:54323] Received: client three
   ```

### ✅ Success Criteria
- Server accepts multiple connections simultaneously
- All clients receive responses
- Server shows active connection count
- No blocking or waiting between clients

---

## 🎲 Activity 4: Random Message Client

### Objective
Test client that sends random number of messages and auto-terminates.

### Steps

1. **Start Server:**
   ```bash
   python server-multithreaded.py
   ```

2. **Run Random Client:**
   ```bash
   python client-random.py
   ```

3. **Observe Output:**
   ```
   Client will send 7 random messages to localhost:12000

   [Message 1/7] Sending: abc def ghi jkl
   [Message 1/7] From Server: ABC DEF GHI JKL

   [Message 2/7] Sending: mno pqr stu
   [Message 2/7] From Server: MNO PQR STU
   ...
   [Message 7/7] Sending: vwx yz
   [Message 7/7] From Server: VWX YZ

   ✓ Successfully sent all 7 messages. Client terminating.
   ```

4. **Run Multiple Times:**
   ```bash
   python client-random.py
   python client-random.py
   python client-random.py
   ```
   Verify different random counts each time.

### ✅ Success Criteria
- Random number of messages (1-10) generated
- Random message content created
- All messages sent successfully
- Client auto-terminates after completion
- Different behavior each run

---

## 🎲🌐 Activity 5: Test Random Client on Different Hosts

### Objective
Combine Activities 2 and 4 - test random client with remote server and concurrent connections.

### Test 5A: Remote Random Client

**Server Machine:**
```bash
python server-multithreaded.py
```

**Client Machine:**
```bash
python client-random.py 192.168.1.100
```

### Test 5B: Multiple Concurrent Random Clients

**Server Machine:**
```bash
python server-multithreaded.py
```

**Client Machine (3 terminals):**
```bash
# Terminal 1
python client-random.py 192.168.1.100

# Terminal 2
python client-random.py 192.168.1.100

# Terminal 3
python client-random.py 192.168.1.100
```

### ✅ Success Criteria
- Random clients work across network
- Multiple random clients can run concurrently
- All messages delivered successfully
- Server handles concurrent random clients

---

## 💻 Activity 6: C++ Implementation

### Objective
Test C++ versions of server and client.

### Steps

1. **Compile C++ Programs:**
   ```bash
   g++ -std=c++11 server-socket.cpp -o server-socket.exe -lws2_32
   g++ -std=c++11 client-socket.cpp -o client-socket.exe -lws2_32
   g++ -std=c++11 client-random.cpp -o client-random.exe -lws2_32
   ```

2. **Test C++ Server + C++ Client:**

   **Terminal 1:**
   ```bash
   ./server-socket.exe
   ```

   **Terminal 2:**
   ```bash
   ./client-socket.exe
   ```

3. **Test C++ Random Client:**
   ```bash
   ./client-random.exe
   ```

4. **Test Concurrent C++ Clients:**
   - Open 3 terminals
   - Run `./client-socket.exe` in each
   - Send messages simultaneously

### ✅ Success Criteria
- C++ programs compile without errors
- C++ server handles connections like Python version
- C++ clients work identically to Python versions
- Multithreading works in C++ server

---

## 🔄 Activity 7: Cross-Language Testing

### Objective
Test all combinations of servers and clients in different languages.

### Test Matrix

#### Test 7.1: Python Server + C++ Client

**Terminal 1:**
```bash
python server-multithreaded.py
```

**Terminal 2:**
```bash
./client-socket.exe
```

**Expected:** ✅ Works - C++ client communicates with Python server

---

#### Test 7.2: Python Server + JavaScript Client

**Terminal 1:**
```bash
python server-multithreaded.py
```

**Terminal 2:**
```bash
node client-socket.js
```

**Expected:** ✅ Works - JavaScript client communicates with Python server

---

#### Test 7.3: C++ Server + Python Client

**Terminal 1:**
```bash
./server-socket.exe
```

**Terminal 2:**
```bash
python client-socket.py
```

**Expected:** ✅ Works - Python client communicates with C++ server

---

#### Test 7.4: C++ Server + JavaScript Client

**Terminal 1:**
```bash
./server-socket.exe
```

**Terminal 2:**
```bash
node client-socket.js
```

**Expected:** ✅ Works - JavaScript client communicates with C++ server

---

#### Test 7.5: Python Server + Mixed Clients (Concurrent)

**Terminal 1:**
```bash
python server-multithreaded.py
```

**Terminal 2:**
```bash
python client-socket.py
```

**Terminal 3:**
```bash
./client-socket.exe
```

**Terminal 4:**
```bash
node client-socket.js
```

**Expected:** ✅ All clients work simultaneously with Python server

---

#### Test 7.6: C++ Server + Mixed Clients (Concurrent)

**Terminal 1:**
```bash
./server-socket.exe
```

**Terminal 2:**
```bash
python client-socket.py
```

**Terminal 3:**
```bash
./client-socket.exe
```

**Terminal 4:**
```bash
node client-socket.js
```

**Expected:** ✅ All clients work simultaneously with C++ server

---

#### Test 7.7: Random Clients Cross-Language

**Python Server + C++ Random Client:**
```bash
# Terminal 1
python server-multithreaded.py

# Terminal 2
./client-random.exe
```

**Python Server + JavaScript Random Client:**
```bash
# Terminal 1
python server-multithreaded.py

# Terminal 2
node client-random.js
```

**C++ Server + Python Random Client:**
```bash
# Terminal 1
./server-socket.exe

# Terminal 2
python client-random.py
```

**C++ Server + JavaScript Random Client:**
```bash
# Terminal 1
./server-socket.exe

# Terminal 2
node client-random.js
```

### ✅ Success Criteria for Activity 7
- All language combinations work correctly
- Protocol compatibility verified
- No encoding or communication issues
- Concurrent mixed-language clients work

---

## 📊 Complete Test Results Checklist

- [ ] Activity 1: Python local testing ✅
- [ ] Activity 2: Remote host testing (Manual) ⚠️
- [ ] Activity 3: Multithreading with 3+ clients ✅
- [ ] Activity 4: Random message client ✅
- [ ] Activity 5: Remote random + concurrent ⚠️
- [ ] Activity 6: C++ compilation and testing ✅
- [ ] Activity 7.1: Python server + C++ client ✅
- [ ] Activity 7.2: Python server + JavaScript client ✅
- [ ] Activity 7.3: C++ server + Python client ✅
- [ ] Activity 7.4: C++ server + JavaScript client ✅
- [ ] Activity 7.5: Mixed concurrent clients (Python server) ✅
- [ ] Activity 7.6: Mixed concurrent clients (C++ server) ✅
- [ ] Activity 7.7: Random clients cross-language ✅

**Legend:**
- ✅ Can be tested locally
- ⚠️ Requires manual testing with two machines

---

## 🎯 Final Verification

After completing all tests, verify:

1. **All Python implementations work** ✅
2. **All C++ implementations work** ✅
3. **All JavaScript implementations work** ✅
4. **Multithreading handles concurrent connections** ✅
5. **Random clients auto-terminate** ✅
6. **Cross-language compatibility verified** ✅
7. **Remote testing documented** ⚠️ (Manual)

---

## 📝 Notes

- Activities 2 and 5 require manual testing with two separate machines
- All other activities can be tested on a single machine
- Use `Ctrl+C` to stop servers
- Check firewall settings if remote connections fail
- All implementations use port 12000 by default
