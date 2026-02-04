#include <iostream>
#include <thread>
#include <vector>
#include <mutex>
#include <string>
#include <cstring>
#include <ctime>
#include <winsock2.h>
#include <ws2tcpip.h>

#pragma comment(lib, "ws2_32.lib")

#define DEFAULT_PORT 8080
#define BUFFER_SIZE 1024
#define MAX_CLIENTS 10

// Variables globales para sincronización
std::mutex client_mutex;
int client_counter = 0;

// Estructura para datos del cliente
struct ClientData {
    SOCKET client_socket;
    int client_id;
    sockaddr_in client_addr;
};

// Función para obtener timestamp formateado
std::string get_timestamp() {
    time_t now = time(nullptr);
    struct tm* t = localtime(&now);
    char buffer[32];
    snprintf(buffer, sizeof(buffer), "%02d:%02d:%02d", 
             t->tm_hour, t->tm_min, t->tm_sec);
    return std::string(buffer);
}

// Función que maneja cada cliente en un hilo separado
void handle_client(ClientData data) {
    SOCKET client_socket = data.client_socket;
    int client_id = data.client_id;
    char buffer[BUFFER_SIZE];
    char client_ip[INET_ADDRSTRLEN];
    int message_count = 0;
    
    // Obtener IP del cliente
    inet_ntop(AF_INET, &(data.client_addr.sin_addr), client_ip, INET_ADDRSTRLEN);
    
    std::cout << "[Cliente " << client_id << "] Conexión establecida desde " 
              << client_ip << ":" << ntohs(data.client_addr.sin_port) << std::endl;
    
    // Recibir mensajes del cliente
    int recv_size;
    while ((recv_size = recv(client_socket, buffer, BUFFER_SIZE - 1, 0)) > 0) {
        buffer[recv_size] = '\0';
        message_count++;
        
        std::cout << "[Cliente " << client_id << "] Mensaje " << message_count 
                  << " recibido (" << get_timestamp() << "): " << buffer << std::endl;
        
        // Crear respuesta
        std::string response = "Servidor: Mensaje " + std::to_string(message_count) + 
                              " recibido (" + std::to_string(recv_size) + " bytes) - '" + 
                              std::string(buffer) + "'";
        
        // Enviar respuesta
        if (send(client_socket, response.c_str(), response.length(), 0) < 0) {
            std::cerr << "[Cliente " << client_id << "] Error al enviar respuesta" << std::endl;
            break;
        }
    }
    
    if (recv_size == 0) {
        std::cout << "[Cliente " << client_id << "] Desconectado. Total de mensajes: " 
                  << message_count << std::endl;
    } else if (recv_size == SOCKET_ERROR) {
        std::cerr << "[Cliente " << client_id << "] Error en recv. Código: " 
                  << WSAGetLastError() << std::endl;
    }
    
    // Cerrar socket del cliente
    closesocket(client_socket);
    
    // Decrementar contador de clientes
    {
        std::lock_guard<std::mutex> lock(client_mutex);
        client_counter--;
        std::cout << "[Servidor] Clientes activos: " << client_counter << std::endl;
    }
}

int main(int argc, char* argv[]) {
    WSADATA wsa;
    SOCKET server_socket, client_socket;
    sockaddr_in server_addr, client_addr;
    int client_addr_len = sizeof(client_addr);
    int port = DEFAULT_PORT;
    int client_id = 0;
    std::vector<std::thread> client_threads;
    
    // Parsear argumentos
    if (argc > 1) {
        port = std::atoi(argv[1]);
    }
    
    // Inicializar Winsock
    std::cout << "Inicializando Winsock..." << std::endl;
    if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0) {
        std::cerr << "Error al inicializar Winsock. Código: " << WSAGetLastError() << std::endl;
        return 1;
    }
    
    // Crear socket
    if ((server_socket = socket(AF_INET, SOCK_STREAM, 0)) == INVALID_SOCKET) {
        std::cerr << "Error al crear socket. Código: " << WSAGetLastError() << std::endl;
        WSACleanup();
        return 1;
    }
    std::cout << "Socket creado." << std::endl;
    
    // Configurar dirección del servidor
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(port);
    
    // Vincular socket
    if (bind(server_socket, (struct sockaddr*)&server_addr, sizeof(server_addr)) == SOCKET_ERROR) {
        std::cerr << "Error en bind. Código: " << WSAGetLastError() << std::endl;
        closesocket(server_socket);
        WSACleanup();
        return 1;
    }
    std::cout << "Socket vinculado al puerto " << port << "." << std::endl;
    
    // Escuchar conexiones
    if (listen(server_socket, MAX_CLIENTS) == SOCKET_ERROR) {
        std::cerr << "Error en listen. Código: " << WSAGetLastError() << std::endl;
        closesocket(server_socket);
        WSACleanup();
        return 1;
    }
    
    std::cout << "Servidor escuchando en el puerto " << port << "..." << std::endl;
    std::cout << "Esperando conexiones de clientes..." << std::endl;
    std::cout << "========================================" << std::endl;
    
    // Aceptar conexiones entrantes
    while (true) {
        client_socket = accept(server_socket, (struct sockaddr*)&client_addr, &client_addr_len);
        
        if (client_socket == INVALID_SOCKET) {
            std::cerr << "Error en accept. Código: " << WSAGetLastError() << std::endl;
            continue;
        }
        
        // Incrementar contador de clientes
        {
            std::lock_guard<std::mutex> lock(client_mutex);
            client_counter++;
            client_id++;
            std::cout << "[Servidor] Nueva conexión aceptada. Clientes activos: " 
                      << client_counter << std::endl;
        }
        
        // Crear estructura de datos para el cliente
        ClientData data;
        data.client_socket = client_socket;
        data.client_id = client_id;
        data.client_addr = client_addr;
        
        // Crear hilo para manejar el cliente
        try {
            std::thread client_thread(handle_client, data);
            client_thread.detach(); // Detach para que el hilo se ejecute independientemente
        } catch (const std::exception& e) {
            std::cerr << "Error al crear hilo para el cliente: " << e.what() << std::endl;
            closesocket(client_socket);
        }
    }
    
    // Limpiar (este código nunca se alcanza en el bucle infinito)
    closesocket(server_socket);
    WSACleanup();
    
    return 0;
}
