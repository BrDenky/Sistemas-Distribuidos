from socket import *
import sys

# Accept server IP from command line argument, default to localhost
if len(sys.argv) > 1:
    serverName = sys.argv[1]
else:
    serverName = "localhost"

serverPort = 12000
next = True

print(f"Connecting to server at {serverName}:{serverPort}")

while next:
    try:
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect((serverName, serverPort))
        sentence = input("Input lowercase sentence: ")
        clientSocket.send(sentence.encode())
        modifiedSentence = clientSocket.recv(1024)
        print("From Server:", modifiedSentence.decode())
        other = input("Other message: (Y/N) ")
        if other.upper() == "N":
            next = False
        clientSocket.close()
    except ConnectionRefusedError:
        print(f"ERROR: Could not connect to server at {serverName}:{serverPort}")
        print("Make sure the server is running and the IP address is correct.")
        break
    except Exception as e:
        print(f"ERROR: {e}")
        break
