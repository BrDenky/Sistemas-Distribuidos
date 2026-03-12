# Part 1: RMI - Complex Number Manager

## Description
This implementation provides a distributed Complex Number Manager using Python's XML-RPC (Remote Method Invocation). The server performs complex number operations (addition, subtraction, multiplication, division) and returns results to clients.

## Files
- `server_complex.py` - RMI server that handles complex number operations
- `client_complex.py` - Interactive client with manual and automatic testing modes

## Complex Number Operations

### Addition
(a + bi) + (c + di) = (a + c) + (b + d)i

### Subtraction
(a + bi) - (c + di) = (a - c) + (b - d)i

### Multiplication
(a + bi) × (c + di) = (ac - bd) + (ad + bc)i

### Division
(a + bi) ÷ (c + di) = [(ac + bd) + (bc - ad)i] / (c² + d²)

## Usage

### Local Testing (Same Machine)

1. **Start the server:**
```bash
python server_complex.py
```

2. **Run the client (in a new terminal):**
```bash
python client_complex.py
```

3. **Use the interactive menu:**
   - Option 1-4: Perform specific operations
   - Option 5: Run automatic test with random numbers
   - Option 6: Exit

### Testing on Different Hosts

1. **On the server machine:**
   - Edit `server_complex.py` line 40: Change `HOST = 'localhost'` to `HOST = '0.0.0.0'`
   - Run: `python server_complex.py`
   - Note the server's IP address

2. **On the client machine:**
   - Edit `client_complex.py` line 14: Change `HOST = 'localhost'` to server's IP address
   - Run: `python client_complex.py`

## Features

- **Manual Input**: Enter custom complex numbers
- **Random Generation**: Automatically generate random complex numbers for testing
- **Automatic Testing**: Test all four operations with one command
- **Error Handling**: Division by zero detection
- **Formatted Output**: Clear display of complex numbers (e.g., "3 + 4i" or "5 - 2i")

## Example Output

```
Complex Number 1: 5 + 3i
Complex Number 2: 2 + 1i

Addition: 7 + 4i
Subtraction: 3 + 2i
Multiplication: 7 + 11i
Division: 2.6 + 0.2i
```

## Requirements
- Python 3.x
- No external libraries required (uses built-in `xmlrpc`)
