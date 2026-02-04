#include <iostream>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <string>
#include <thread>
#include <chrono>

#pragma comment(lib, "ws2_32.lib")

using namespace std;

void handleClient(SOCKET clientSocket, sockaddr_in clientAddr) {
    char clientIP[INET_ADDRSTRLEN];
    inet_ntop(AF_INET, &(clientAddr.sin_addr), clientIP, INET_ADDRSTRLEN);
    int clientPort = ntohs(clientAddr.sin_port);
    
    cout << "[NEW CONNECTION] Client connected from: " << clientIP << ":" << clientPort << endl;
    
    try {
        char buffer[1024] = {0};
        int bytesReceived = recv(clientSocket, buffer, sizeof(buffer), 0);
        
        if (bytesReceived > 0) {
            string message(buffer, bytesReceived);
            cout << "[" << clientIP << ":" << clientPort << "] Received: " << message << endl;
            
            // Convert to uppercase
            string upperMessage = message;
            for (char &c : upperMessage) {
                c = toupper(c);
            }
            
            // Simulate processing time
            this_thread::sleep_for(chrono::seconds(3));
            
            // Send response
            send(clientSocket, upperMessage.c_str(), upperMessage.length(), 0);
            cout << "[" << clientIP << ":" << clientPort << "] Response sent" << endl;
        }
    } catch (exception &e) {
        cerr << "[ERROR] " << clientIP << ":" << clientPort << ": " << e.what() << endl;
    }
    
    closesocket(clientSocket);
    cout << "[DISCONNECTED] " << clientIP << ":" << clientPort << endl;
}

int main() {
    WSADATA wsaData;
    int result;
    
    // Initialize Winsock
    result = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if (result != 0) {
        cerr << "WSAStartup failed: " << result << endl;
        return 1;
    }
    
    // Create socket
    SOCKET serverSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (serverSocket == INVALID_SOCKET) {
        cerr << "Socket creation failed: " << WSAGetLastError() << endl;
        WSACleanup();
        return 1;
    }
    
    // Bind socket
    sockaddr_in serverAddr;
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_addr.s_addr = INADDR_ANY;
    serverAddr.sin_port = htons(12000);
    
    if (bind(serverSocket, (sockaddr*)&serverAddr, sizeof(serverAddr)) == SOCKET_ERROR) {
        cerr << "Bind failed: " << WSAGetLastError() << endl;
        closesocket(serverSocket);
        WSACleanup();
        return 1;
    }
    
    // Listen for connections
    if (listen(serverSocket, 5) == SOCKET_ERROR) {
        cerr << "Listen failed: " << WSAGetLastError() << endl;
        closesocket(serverSocket);
        WSACleanup();
        return 1;
    }
    
    cout << "The C++ multithreaded server is ready to receive on port 12000" << endl;
    
    // Accept connections in a loop
    while (true) {
        sockaddr_in clientAddr;
        int clientAddrSize = sizeof(clientAddr);
        SOCKET clientSocket = accept(serverSocket, (sockaddr*)&clientAddr, &clientAddrSize);
        
        if (clientSocket == INVALID_SOCKET) {
            cerr << "Accept failed: " << WSAGetLastError() << endl;
            continue;
        }
        
        // Handle client in a new thread
        thread clientThread(handleClient, clientSocket, clientAddr);
        clientThread.detach();
    }
    
    // Cleanup
    closesocket(serverSocket);
    WSACleanup();
    
    return 0;
}
