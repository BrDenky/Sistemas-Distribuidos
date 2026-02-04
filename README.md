# Network Socket Programming Laboratory
## Complete Workshop - All Activities (1-7)

This repository contains complete implementations for a network socket programming laboratory, including Python, C++, and JavaScript versions with multithreading support.

---

## 📁 Project Structure

```
Sistemas/
├── Python Files
│   ├── server-socket.py              # Original single-threaded server
│   ├── server-multithreaded.py       # Multithreaded server
│   ├── client-socket.py              # Original interactive client
│   └── client-random.py              # Random message client
│
├── C Files
│   ├── server-socket.cpp             # C multithreaded server
│   ├── client-socket.cpp             # C interactive client
│   └── client-random.cpp             # C random message client
│
└── Documentation
    └── README.md                     # This file
```
## 💻 Compilation and Execution

### Compile C files

To compile the C files, use the following command:
```bash
gcc <filename>.c -o <filename> -lws2_32
```

### Run the server

To run the server:
```bash
./<filename>.exe
```

### Run the client

To run the client:
```bash
./<filename>.exe
```
