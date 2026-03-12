# Part 1: Coordination through UTC Server

Este directorio contiene la implementación de un sistema de coordinación de relojes utilizando un servidor de Tiempo Universal Coordinado (UTC) centralizado.

## Funcionalidad
El sistema simula cómo los nodos (clientes) sincronizan su tiempo pidiéndolo a un servidor maestro único. El código implementado cuenta con validaciones de entrada para los puertos, manejo de excepciones de red, y previene bloqueos por caídas del servidor usando _Timeouts_ con la librería `zmq`.

### Archivos:
- `server-UTC.py`: Actúa como el servidor central en el puerto `5000` devolviendo la hora actual de la máquina host en formato UTC.
- `client-UTC.py`: Genera hilos que actúan como procesos clientes, se conectan al servidor y piden la hora para mostrarla en consola.

## ¿Cómo hacer las pruebas?

1. **Abre una nueva terminal** y ejecuta el servidor de la siguiente manera:
   ```bash
   python server-UTC.py --port 5000
   ```
2. **Abre otra terminal** y ejecuta los clientes:
   ```bash
   python client-UTC.py --host localhost --port 5000 --clients 3
   ```
   
### ¿Qué se espera?
Deberías visualizar en la terminal del cliente cómo los hilos hacen las solicitudes. El servidor debe imprimir en su terminal que ha despachado la hora en formato `%Y-%m-%d %H:%M:%S`.

Adicionalmente, si cierras el servidor con `Ctrl+C` (Manejo de excepciones implementado) y corres nuevamente un cliente, este después de pedir la solicitud te indicará mediante la alerta de *Timeout Error* que el servidor está inactivo sin que el programa se quede congelado (bloqueado/deadlock).
