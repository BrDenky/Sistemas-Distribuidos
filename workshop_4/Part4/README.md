# Part 4: Mutual Exclusion

Este directorio incluye la implementación de **Exclusión Mutua** en arquitectura de Sistemas Distribuidos. Se encarga de prevenir que nodos dispares operen sobre la misma franja o sección crítica compartida al mismo tiempo, lo que corrompería la información.

## Funcionalidad
Se aborda la problemática desde dos (2) perspectivas solicitadas:

1. **Gestión de Servidor de Recursos Central (Centralized Approach)**
   - Un único servidor maestro tiene la propiedad de una bandera booleana global. Los procesos clientes le envían la señal para solicitar poder usarlo.
   - El maestro concede, y nadie más puede tener la aprobación sino hasta que el nodo actual le comunique al maestro que ha soltado (`RELEASE`) el recurso.
   - *Archivos:* `resource-server.py` y `process-node.py`.
2. **Distribución mediante Anillo de Tokens (Token Ring Approach)**
   - No existe la figura del servidor central. Todos los nodos están conectados formando un anillo lógico $(0 \rightarrow 1 \rightarrow 2 \rightarrow 0)$.
   - Hay existencia de un `Token` circulante. Todo el tiempo los nodos se lo pasan el uno al otro en círculo.
   - Quien ostenta el token es el ÚNICO que tiene permiso para ejecutar sus rutinas exclusivas antes de pasarlo al nodo siguiente.
   - *Archivos:* `token-ring-node.py`.

## ¿Cómo hacer las pruebas?

### Para probar el enfoque Centralizado
Primero enciende el que gestiona y cuida las peticiones:
```bash
python resource-server.py
```
Luego corre múltiples clientes en otros comandos o terminales a la vez para ver la cola de espera:
```bash
python process-node.py 111
python process-node.py 222
```
*Si no pasas un ID en los flags por la consola, este asignará uno numérico al azar para que pueda identificar quién lo pidió.*

### Para probar el Token Ring
Abre 4 terminales independientes y lanza la secuencia rápidamente:

```bash
# Consola 1
python token-ring-node.py 0   # ← Él generará el primer token global.

# Consola 2
python token-ring-node.py 1 

# Consola 3
python token-ring-node.py 2 

# Consola 4
python token-ring-node.py 3 
```

### ¿Qué se espera?
En el entorno **Centralizado**, verás que el maestro dice "GRANTED" al primer proceso que llegó, y "DENIED" o los pone a esperar a los posteriores hasta que reciban su debida validación afirmativa del acceso.
En el entorno del **Anillo**, verás intermitentemente en pantalla cómo una terminal despliega bloque visual temporal de `---- TOKEN RECEIVED ----`, para luego el siguiente hilo lanzar la notificación de `Passing token to Node {X}`, formando una iteración circular contínua y ordenada donde ocurren las concurrencias.
