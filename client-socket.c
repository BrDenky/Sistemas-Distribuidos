#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <time.h>

#pragma comment(lib, "ws2_32.lib")

#define DEFAULT_PORT 8080
#define BUFFER_SIZE 1024
#define MAX_MESSAGE_LENGTH 256

// Función para generar un mensaje aleatorio
void generate_random_message(char *buffer, int max_length) {
    const char *words[] = {
        "Hello", "World", "Socket", "Programming", "Network",
        "Client", "Server", "Message", "Random", "Data",
        "Communication", "Protocol", "TCP", "UDP", "Connection"
    };
    int num_words = sizeof(words) / sizeof(words[0]);
    
    int word_count = (rand() % 5) + 1;
    buffer[0] = '\0';
    
    for (int i = 0; i < word_count; i++) {
        int word_index = rand() % num_words;
        strcat(buffer, words[word_index]);
        if (i < word_count - 1) {
            strcat(buffer, " ");
        }
    }
}

int main(int argc, char *argv[]) {
    WSADATA wsa;
    SOCKET client_socket;
    struct sockaddr_in server_addr;
    char buffer[BUFFER_SIZE];
    char message[MAX_MESSAGE_LENGTH];
    int port = DEFAULT_PORT;
    char *server_ip = "127.0.0.1";
    int num_messages = 5;
    
    // Parsear argumentos de línea de comandos
    if (argc > 1) {
        server_ip = argv[1];
    }
    if (argc > 2) {
        port = atoi(argv[2]);
    }
    if (argc > 3) {
        num_messages = atoi(argv[3]);
    }
    
    // Inicializar Winsock
    printf("Inicializando Winsock...\n");
    if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0) {
        fprintf(stderr, "Error al inicializar Winsock. Código de error: %d\n", WSAGetLastError());
        return 1;
    }
    
    // Crear socket
    if ((client_socket = socket(AF_INET, SOCK_STREAM, 0)) == INVALID_SOCKET) {
        fprintf(stderr, "Error al crear socket. Código de error: %d\n", WSAGetLastError());
        WSACleanup();
        return 1;
    }
    printf("Socket creado.\n");
    
    // Configurar dirección del servidor
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    server_addr.sin_addr.s_addr = inet_addr(server_ip);
    
    // Conectar al servidor
    printf("Conectando a %s:%d...\n", server_ip, port);
    if (connect(client_socket, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        fprintf(stderr, "Error al conectar. Código de error: %d\n", WSAGetLastError());
        closesocket(client_socket);
        WSACleanup();
        return 1;
    }
    printf("Conectado al servidor.\n");
    
    // Inicializar generador de números aleatorios
    srand(time(NULL));
    
    // Enviar mensajes al servidor
    for (int i = 0; i < num_messages; i++) {
        // Generar mensaje aleatorio
        generate_random_message(message, MAX_MESSAGE_LENGTH);
        
        printf("\nEnviando mensaje %d: %s\n", i + 1, message);
        
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
            printf("Respuesta del servidor: %s\n", buffer);
        }
        
        // Pequeña pausa entre mensajes
        Sleep(500);
    }
    
    // Cerrar socket
    closesocket(client_socket);
    WSACleanup();
    
    printf("\nCliente finalizado.\n");
    return 0;
}
