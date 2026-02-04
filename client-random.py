from socket import *
import random
import string
import sys

# Accept server IP from command line argument, default to localhost
if len(sys.argv) > 1:
    serverName = sys.argv[1]
else:
    serverName = "localhost"

serverPort = 12000

def generate_random_message(length=20):
    """Generate a random message with letters and spaces"""
    chars = string.ascii_lowercase + ' '
    return ''.join(random.choice(chars) for _ in range(length))

# Generate random number of messages (between 1 and 10)
num_messages = random.randint(1, 10)
print(f"Client will send {num_messages} random messages to {serverName}:{serverPort}")

try:
    for i in range(num_messages):
        # Create new socket for each message
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect((serverName, serverPort))
        
        # Generate and send random message
        message = generate_random_message(random.randint(10, 30))
        print(f"\n[Message {i+1}/{num_messages}] Sending: {message}")
        clientSocket.send(message.encode())
        
        # Receive response
        modifiedMessage = clientSocket.recv(1024)
        print(f"[Message {i+1}/{num_messages}] From Server: {modifiedMessage.decode()}")
        
        clientSocket.close()
    
    print(f"\n✓ Successfully sent all {num_messages} messages. Client terminating.")
    
except ConnectionRefusedError:
    print(f"ERROR: Could not connect to server at {serverName}:{serverPort}")
    print("Make sure the server is running and the IP address is correct.")
except Exception as e:
    print(f"ERROR: {e}")
