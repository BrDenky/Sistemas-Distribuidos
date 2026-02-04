#include <iostream>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <string>
#include <cstdlib>
#include <ctime>

#pragma comment(lib, "ws2_32.lib")

using namespace std;

string generateRandomMessage(int length) {
    const string chars = "abcdefghijklmnopqrstuvwxyz ";
    string message;
    for (int i = 0; i < length; i++) {
        message += chars[rand() % chars.length()];
    }
    return message;
}

int main(int argc, char* argv[]) {
    WSADATA wsaData;
    int result;
    
    // Seed random number generator
    srand(time(NULL));
    
    // Get server name from command line or use localhost
    string serverName = "127.0.0.1";
    if (argc > 1) {
        serverName = argv[1];
    }
    
    int serverPort = 12000;
    
    // Initialize Winsock
    result = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if (result != 0) {
        cerr << "WSAStartup failed: " << result << endl;
        return 1;
    }
    
    // Generate random number of messages (1-10)
    int numMessages = (rand() % 10) + 1;
    cout << "Client will send " << numMessages << " random messages to " 
         << serverName << ":" << serverPort << endl;
    
    for (int i = 0; i < numMessages; i++) {
        // Create socket
        SOCKET clientSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
        if (clientSocket == INVALID_SOCKET) {
            cerr << "Socket creation failed: " << WSAGetLastError() << endl;
            WSACleanup();
            return 1;
        }
        
        // Setup server address
        sockaddr_in serverAddr;
        serverAddr.sin_family = AF_INET;
        serverAddr.sin_port = htons(serverPort);
        
        // Convert IP address
        if (inet_pton(AF_INET, serverName.c_str(), &serverAddr.sin_addr) <= 0) {
            cerr << "Invalid address: " << serverName << endl;
            closesocket(clientSocket);
            WSACleanup();
            return 1;
        }
        
        // Connect to server
        if (connect(clientSocket, (sockaddr*)&serverAddr, sizeof(serverAddr)) == SOCKET_ERROR) {
            cerr << "Connection failed: " << WSAGetLastError() << endl;
            cerr << "Make sure the server is running at " << serverName << ":" << serverPort << endl;
            closesocket(clientSocket);
            WSACleanup();
            return 1;
        }
        
        // Generate and send random message
        int messageLength = (rand() % 21) + 10; // 10-30 characters
        string message = generateRandomMessage(messageLength);
        
        cout << "\n[Message " << (i+1) << "/" << numMessages << "] Sending: " << message << endl;
        send(clientSocket, message.c_str(), message.length(), 0);
        
        // Receive response
        char buffer[1024] = {0};
        int bytesReceived = recv(clientSocket, buffer, sizeof(buffer), 0);
        
        if (bytesReceived > 0) {
            string response(buffer, bytesReceived);
            cout << "[Message " << (i+1) << "/" << numMessages << "] From Server: " << response << endl;
        }
        
        closesocket(clientSocket);
    }
    
    cout << "\n✓ Successfully sent all " << numMessages << " messages. Client terminating." << endl;
    
    WSACleanup();
    return 0;
}
