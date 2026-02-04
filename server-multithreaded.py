from socket import *
import threading
import time

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(("", serverPort))
serverSocket.listen(5)  # Increased backlog for multiple connections
print("The multithreaded server is ready to receive")

def handle_client(connectionSocket, addr):
    """Handle individual client connection in a separate thread"""
    try:
        print(f"[NEW CONNECTION] Client connected from: {addr}")
        sentence = connectionSocket.recv(1024).decode()
        print(f"[{addr}] Received: {sentence}")
        capitalizedSentence = sentence.upper()
        time.sleep(3)  # Simulate processing time
        connectionSocket.send(capitalizedSentence.encode())
        print(f"[{addr}] Response sent")
    except Exception as e:
        print(f"[ERROR] {addr}: {e}")
    finally:
        connectionSocket.close()
        print(f"[DISCONNECTED] {addr}")

# Main server loop
while True:
    connectionSocket, addr = serverSocket.accept()
    # Create a new thread for each client connection
    client_thread = threading.Thread(target=handle_client, args=(connectionSocket, addr))
    client_thread.start()
    print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
