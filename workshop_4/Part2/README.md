# Part 2: Global Time without a UTC Server

Esta sección demuestra cómo coordinar el tiempo global a lo largo de nodos paralelos sin un servidor central que sirva como "fuente de la verdad". 

## Funcionalidad
Esta implementación utiliza un algoritmo de promedio. Cada nodo consulta el tiempo del sistema actual del resto de sus pares en la red, realiza un promedio entre la hora externa y la propia, y ajusta su reloj local a ese valor. Se añadió un efecto de `drift` (desviación) aleatoria cada cierto número de ciclos ($k = 10$) para simular que los relojes de las máquinas físicas tienden a atrasarse o adelantarse con el tiempo.

### Archivos:
- `peer-node.py`: Archivo principal. Despliega dos *threads* (hilos), uno que actúa como servidor pasivo esperando a que le pregunten la hora, y otro como cliente que constantemente envía *request* a los puertos del resto de sus nodos primos.

## ¿Qué arreglos se hicieron?
Originalmente un nodo dependía de que **todos** los otros estuvieran conectados antes de operar; si faltaba uno, se formaba un _deadlock_. Ahora, se aplican `Timeouts` a nivel *socket*, por lo tanto, un nodo puede empezar a trabajar operando promedios solo sobre los nodos que sí le contestaron.

## ¿Cómo hacer las pruebas?

Para emular este algoritmo correctamente necesitas simular múltiples máquinas corriendo en paralelo.

Abre 4 terminales independientes en esta carpeta e inicializa los nodos usando un `ID` diferente para cada terminal que designe el puerto en base al `6000 + ID`:

**Terminal 1:**
```bash
python peer-node.py
# Introduce 0 cuando pregunte el ID
```
**Terminal 2:**
```bash
python peer-node.py
# Introduce 1 cuando pregunte el ID
```

Haz esto consecutivamente con los ID `2` y `3`.

### ¿Qué se espera?
Notarás cómo los nodos imprimen los tiempos promedio. Al ir encendiendo más terminales, los promedios globales confluirán (serán muy cercanos o idénticos). Cada 10 ciclos observaremos el texto: `Clock drift applied` desviando el valor del tiempo interno.
