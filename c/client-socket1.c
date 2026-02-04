#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <winsock2.h>
#include <ws2tcpip.h>

#pragma comment(lib, "ws2_32.lib")

#define DEFAULT_PORT 12000
#define BUFFER_SIZE 1024
#define MAX_MESSAGE_LENGTH 256

int main(int argc, char *argv[]) {
    WSADATA wsa;
    SOCKET client_socket;
    struct sockaddr_in server_addr;
    char buffer[BUFFER_SIZE];
    char message[MAX_MESSAGE_LENGTH];
    int port = DEFAULT_PORT;
    char *server_ip = "172.23.198.200";
    
    if (argc > 1) {
        port = atoi(argv[1]);
    }
    
    printf("Inicializando Winsock...\n");
    if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0) {
        fprintf(stderr, "Error al inicializar Winsock. Código de error: %d\n", WSAGetLastError());
        return 1;
    }
    
    if ((client_socket = socket(AF_INET, SOCK_STREAM, 0)) == INVALID_SOCKET) {
        fprintf(stderr, "Error al crear socket. Código de error: %d\n", WSAGetLastError());
        WSACleanup();
        return 1;
    }
    printf("Socket creado.\n");
    
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    server_addr.sin_addr.s_addr = inet_addr(server_ip);
    
    printf("Conectando a %s:%d...\n", server_ip, port);
    if (connect(client_socket, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        fprintf(stderr, "Error al conectar. Código de error: %d\n", WSAGetLastError());
        closesocket(client_socket);
        WSACleanup();
        return 1;
    }
    printf("Conectado al servidor.\n");
    
    while (1) {
        printf("Escribe tu mensaje: ");
        fgets(message, MAX_MESSAGE_LENGTH, stdin);
        
        // Eliminar el salto de línea
        message[strcspn(message, "\n")] = 0;
        
        // Verificar si quiere salir
        if (strcmp(message, "salir") == 0) {
            printf("Cerrando conexión...\n");
            break;
        }
        
        // Enviar mensaje
        if (send(client_socket, message, strlen(message), 0) < 0) {
            fprintf(stderr, "Error al enviar mensaje. Código de error: %d\n", WSAGetLastError());
            break;
        }
        
        // Recibir respuesta
        memset(buffer, 0, BUFFER_SIZE);
        int recv_size = recv(client_socket, buffer, BUFFER_SIZE - 1, 0);
        
        if (recv_size == SOCKET_ERROR) {
            fprintf(stderr, "Error al recibir respuesta. Código de error: %d\n", WSAGetLastError());
            break;
        } else if (recv_size == 0) {
            printf("Servidor cerró la conexión.\n");
            break;
        } else {
            buffer[recv_size] = '\0';
            printf("Respuesta del servidor: %s\n\n", buffer);
        }
    }
    
    closesocket(client_socket);
    WSACleanup();
    
    printf("Cliente finalizado.\n");
    return 0;
}