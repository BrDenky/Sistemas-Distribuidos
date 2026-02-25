#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAX_MESSAGE_LENGTH 256
#define NUM_MESSAGES 10

// Función para generar un mensaje aleatorio
void generate_random_message(char *buffer, int max_length) {
    const char *words[] = {
        "Hello", "World", "Socket", "Programming", "Network",
        "Client", "Server", "Message", "Random", "Data",
        "Communication", "Protocol", "TCP", "UDP", "Connection"
    };
    int num_words = sizeof(words) / sizeof(words[0]);
    
    // Generar entre 1 y 5 palabras
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
    char message[MAX_MESSAGE_LENGTH];
    int num_messages = NUM_MESSAGES;
    
    // Inicializar generador de números aleatorios
    srand(time(NULL));
    
    // Si se proporciona un argumento, usarlo como número de mensajes
    if (argc > 1) {
        num_messages = atoi(argv[1]);
        if (num_messages <= 0) {
            fprintf(stderr, "Error: El número de mensajes debe ser positivo\n");
            return 1;
        }
    }
    
    printf("Generando %d mensajes aleatorios:\n", num_messages);
    printf("=====================================\n");
    
    for (int i = 0; i < num_messages; i++) {
        generate_random_message(message, MAX_MESSAGE_LENGTH);
        printf("Mensaje %d: %s\n", i + 1, message);
    }
    
    return 0;
}
