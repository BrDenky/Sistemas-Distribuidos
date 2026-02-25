#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <process.h>
#include <time.h>

#pragma comment(lib, "ws2_32.lib")

#define DEFAULT_PORT 12000
#define BUFFER_SIZE 1024
#define MAX_CLIENTS 10

typedef struct {
    SOCKET client_socket;
    int client_id;
    struct sockaddr_in client_addr;
} client_data_t;

static int client_counter = 0;
static CRITICAL_SECTION cs;

void to_uppercase(char *str) {
    for (int i = 0; str[i] != '\0'; i++) {
        if (str[i] >= 'a' && str[i] <= 'z') {
            str[i] = str[i] - 32;
        }
    }
}

unsigned __stdcall handle_client(void *arg) {
    client_data_t *data = (client_data_t *)arg;
    SOCKET client_socket = data->client_socket;
    int client_id = data->client_id;
    char client_ip[INET_ADDRSTRLEN];
    char buffer[BUFFER_SIZE];
    char response[BUFFER_SIZE];
    int recv_size;
    int message_count = 0;
    
    inet_ntop(AF_INET, &(data->client_addr.sin_addr), client_ip, INET_ADDRSTRLEN);
    
    printf("[Cliente %d] Conexion establecida desde %s:%d\n", 
           client_id, client_ip, ntohs(data->client_addr.sin_port));
    
    while ((recv_size = recv(client_socket, buffer, BUFFER_SIZE - 1, 0)) > 0) {
        buffer[recv_size] = '\0';
        message_count++;
        

        time_t now = time(NULL);
        struct tm *t = localtime(&now);
        
        printf("[Cliente %d] Mensaje %d recibido (%02d:%02d:%02d): %s\n", 
               client_id, message_count, t->tm_hour, t->tm_min, t->tm_sec, buffer);

        to_uppercase(buffer);
        
        snprintf(response, BUFFER_SIZE, "%s", buffer);
        

        if (send(client_socket, response, strlen(response), 0) < 0) {
            fprintf(stderr, "[Cliente %d] Error al enviar respuesta\n", client_id);
            break;
        }
    }
    
    if (recv_size == 0) {
        printf("[Cliente %d] Desconectado.  %d\n", 
               client_id, message_count);
    } else if (recv_size == SOCKET_ERROR) {
        fprintf(stderr, "[Cliente %d] Error en recv. Código: %d\n", 
                client_id, WSAGetLastError());
    }
    

    closesocket(client_socket);
    free(data);
    
 
    EnterCriticalSection(&cs);
    client_counter--;
    printf("Clientes activos: %d\n", client_counter);
    LeaveCriticalSection(&cs);
    
    return 0;
}

int main(int argc, char *argv[]) {
    WSADATA wsa;
    SOCKET server_socket, client_socket;
    struct sockaddr_in server_addr, client_addr;
    int client_addr_len = sizeof(client_addr);
    int port = DEFAULT_PORT;
    int client_id = 0;
    
    if (argc > 1) {
        port = atoi(argv[1]);
    }
    

    InitializeCriticalSection(&cs);
    

 
    if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0) {
        fprintf(stderr, "Error al inicializar Winsock. Código: %d\n", WSAGetLastError());
        return 1;
    }
    

    if ((server_socket = socket(AF_INET, SOCK_STREAM, 0)) == INVALID_SOCKET) {
        fprintf(stderr, "Error al crear socket. Código: %d\n", WSAGetLastError());
        WSACleanup();
        return 1;
    }

    

    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(port);
    

    if (bind(server_socket, (struct sockaddr *)&server_addr, sizeof(server_addr)) == SOCKET_ERROR) {
        fprintf(stderr, "Error en bind. Código: %d\n", WSAGetLastError());
        closesocket(server_socket);
        WSACleanup();
        return 1;
    }

    
    if (listen(server_socket, MAX_CLIENTS) == SOCKET_ERROR) {
        fprintf(stderr, "Error en listen. Código: %d\n", WSAGetLastError());
        closesocket(server_socket);
        WSACleanup();
        return 1;
    }
    

    

    while (1) {
        client_socket = accept(server_socket, (struct sockaddr *)&client_addr, &client_addr_len);
        
        if (client_socket == INVALID_SOCKET) {
            fprintf(stderr, "Error en accept. Código: %d\n", WSAGetLastError());
            continue;
        }

        EnterCriticalSection(&cs);
        client_counter++;
        client_id++;
        int current_clients = client_counter;
        int current_id = client_id;
        LeaveCriticalSection(&cs);
        
        printf("[ Nueva conexion aceptada. %d\n", current_clients);
        

        client_data_t *data = (client_data_t *)malloc(sizeof(client_data_t));
        if (data == NULL) {
            fprintf(stderr, "Error al asignar memoria para datos del cliente\n");
            closesocket(client_socket);
            continue;
        }
        
        data->client_socket = client_socket;
        data->client_id = current_id;
        data->client_addr = client_addr;
        

        HANDLE thread = (HANDLE)_beginthreadex(NULL, 0, handle_client, data, 0, NULL);
        
        if (thread == 0) {
            fprintf(stderr, "Error al crear hilo para el cliente\n");
            closesocket(client_socket);
            free(data);
        } else {
            CloseHandle(thread);
        }
    }
    
    closesocket(server_socket);
    WSACleanup();
    DeleteCriticalSection(&cs);
    
    return 0;
}