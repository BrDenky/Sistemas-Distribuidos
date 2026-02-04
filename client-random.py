from socket import *
import random
import string
import sys

serverName = "172.23.198.200"

serverPort = 12000

def generate_random_message(num_words=5):
    words = [
        'el', 'la', 'un', 'una', 'gato', 'perro', 'casa', 'libro', 
        'corre', 'salta', 'lee', 'escribe', 'rápido', 'lento',
        'grande', 'pequeño', 'azul', 'rojo', 'en', 'con', 'por'
    ]
    message = ' '.join(random.choice(words) for _ in range(4))
    return message + '.'

# Generate random number of messages (between 1 and 10)
num_messages = random.randint(1, 10)

try:
    for i in range(num_messages):
        clientSocket = socket(AF_INET, SOCK_STREAM) # Create a new socket for each message
        clientSocket.connect((serverName, serverPort))
        
        message = generate_random_message(random.randint(10, 30)) # Generate and send random message
        print(f"\n[Message {i+1}/{num_messages}] Sending: {message}")
        clientSocket.send(message.encode())
        
        modifiedMessage = clientSocket.recv(1024) # Receive response
        print(f"[Message {i+1}/{num_messages}] From Server: {modifiedMessage.decode()}")
        
        clientSocket.close()

except ConnectionRefusedError:
    print(f"ERROR: Could not connect to server at {serverName}:{serverPort}")
    print("Make sure the server is running and the IP address is correct.")
except Exception as e:
    print(f"ERROR: {e}")
