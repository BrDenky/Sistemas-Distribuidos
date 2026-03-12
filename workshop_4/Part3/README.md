# Part 3: Vector Clocks

Este sub-taller demuestra el uso de un **Reloj Vectorial** (Vector Clocks) para modelar y preservar el concepto del *ordenamiento causal* y acontecimiento de eventos distribuidos.

## Funcionalidad
A diferencia del tiempo universal, aquí a cada nodo no le importa "la hora", sino tener un arreglo numérico (vector) equivalente al número total de los procesos conectados al sistema.

- Cada vez que un nodo hace algo, aumenta su propia métrica en la posición $i$ del arreglo (`+1`).
- Posteriormente le envía dicho vector a sus pares.
- Cuando los otros pares lo reciben, ajustan su propio vector comparando posición a posición cuál es el valor numérico más grande `$max(mio[i], ajeno[i])$` y finalmente actualizan el reloj.

### Archivos:
- `vector-clock.py`: Contiene los hilos cliente-servidor encargados de pedir y mandar arreglos y procesar las variables compartidas del vector. También está programado con `Timeouts` y control de excepciones (para que si el nodo `2` no está encendido, el nodo `0` y `1` aún puedan conversar).

## ¿Cómo hacer las pruebas?

Abre diferentes consolas o terminales para levantar múltiples procesos en paralelo:

**Terminal 1:**
```bash
python vector-clock.py
# Introduce 0
```
**Terminal 2:**
```bash
python vector-clock.py
# Introduce 1
```

### ¿Qué se espera?
A medida que pasen los segundos notarás como cada consola imprime la información `Process X received reply: [x, y, z...]`.
Al comparar visualmente varias de las terminales notarás cómo los relojes vectoriales de todos los procesos se mantienen en el registro consistente con base a los mensajes causales enviados entre ellos, permitiendo llevar un flujo rastreable de las acciones.
