# Compiling and Running C++ Socket Programs on Windows

This guide explains how to compile and run the C++ socket programs for this laboratory.

## Prerequisites

You need a C++ compiler that supports C++11 or later. Options include:

### Option 1: MinGW-w64 (Recommended)
1. Download MinGW-w64 from: https://www.mingw-w64.org/
2. Install and add to PATH
3. Verify installation: `g++ --version`

### Option 2: Microsoft Visual Studio
1. Install Visual Studio with C++ development tools
2. Use Developer Command Prompt

### Option 3: MSYS2
1. Install MSYS2 from: https://www.msys2.org/
2. Install compiler: `pacman -S mingw-w64-x86_64-gcc`

## Compilation Commands

### Using g++ (MinGW or MSYS2)

**Compile Server:**
```bash
g++ -std=c++11 server-socket.cpp -o server-socket.exe -lws2_32
```

**Compile Client:**
```bash
g++ -std=c++11 client-socket.cpp -o client-socket.exe -lws2_32
```

**Compile Random Client:**
```bash
g++ -std=c++11 client-random.cpp -o client-random.exe -lws2_32
```

### Using Visual Studio Developer Command Prompt

**Compile Server:**
```bash
cl server-socket.cpp /EHsc /link ws2_32.lib
```

**Compile Client:**
```bash
cl client-socket.cpp /EHsc /link ws2_32.lib
```

**Compile Random Client:**
```bash
cl client-random.cpp /EHsc /link ws2_32.lib
```

## Running the Programs

### Server
```bash
# Run the compiled server
./server-socket.exe
```

### Interactive Client
```bash
# Connect to localhost
./client-socket.exe

# Connect to remote server
./client-socket.exe 192.168.1.100
```

### Random Message Client
```bash
# Connect to localhost
./client-random.exe

# Connect to remote server
./client-random.exe 192.168.1.100
```

## Troubleshooting

### "ws2_32.lib not found"
- Make sure you include `-lws2_32` flag when using g++
- For Visual Studio, use `/link ws2_32.lib`

### "Winsock initialization failed"
- This usually indicates a system issue
- Try running as administrator

### "Connection refused"
- Make sure the server is running first
- Check that port 12000 is not blocked by firewall
- Verify the IP address is correct

### Firewall Issues
If testing between different machines:
1. Open Windows Firewall settings
2. Allow incoming connections on port 12000
3. Or temporarily disable firewall for testing (not recommended for production)

## Notes

- The `-std=c++11` flag enables C++11 features (threads, etc.)
- The `-lws2_32` flag links the Windows Socket library
- All programs use port 12000 by default
- Server binds to all interfaces (0.0.0.0)
- Clients can specify server IP as command-line argument
