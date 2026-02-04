#include <iostream>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <string>

#pragma comment(lib, "ws2_32.lib")

using namespace std;

int main(int argc, char* argv[]) {
    WSADATA wsaData;
    int result;
    
    // Get server name from command line or use localhost
    string serverName = "172.23.198.200";
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
    
    cout << "Connecting to server at " << serverName << ":" << serverPort << endl;
    
    bool next = true;
    while (next) {
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
        
        // Get message from user
        cout << "Input lowercase sentence: ";
        string sentence;
        getline(cin, sentence);
        
        // Send message
        send(clientSocket, sentence.c_str(), sentence.length(), 0);
        
        // Receive response
        char buffer[1024] = {0};
        int bytesReceived = recv(clientSocket, buffer, sizeof(buffer), 0);
        
        if (bytesReceived > 0) {
            string response(buffer, bytesReceived);
            cout << "From Server: " << response << endl;
        }
        
        // Ask if user wants to send another message
        cout << "Other message: (Y/N) ";
        string other;
        getline(cin, other);
        
        if (other == "N" || other == "n") {
            next = false;
        }
        
        closesocket(clientSocket);
    }
    
    WSACleanup();
    return 0;
}
