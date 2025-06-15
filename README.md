# 🚢 Simulación "Hundir la flota" usando computación paralela

## 🧠 1. Introducción y contexto

Este proyecto implementa una simulación del clásico juego de **Hundir la flota** (también conocido como *Battleship*), usando **computación paralela** a través de la librería **MPI (Message Passing Interface)** en Python. El propósito principal es estudiar y poner en práctica los conceptos clave de la computación distribuida, como la comunicación entre procesos, la sincronización y la separación de tareas entre distintos nodos de procesamiento.

La implementación está diseñada para ejecutarse con exactamente **dos procesos MPI**, donde cada proceso controla un jugador distinto. Cada jugador:

* Gestiona su propio tablero y su flota de barcos.
* Decide en cada turno dónde disparar.
* Recibe disparos del oponente y responde con el resultado (agua, tocado o hundido).

Además del juego en sí, se han implementado múltiples **estrategias de juego** que permiten comparar cómo varían los resultados en función del comportamiento inteligente de cada jugador. Esto permite analizar de forma sistemática el rendimiento de cada estrategia en entornos enfrentados.

### Objetivos del proyecto

* Simular partidas de *Hundir la flota* con distintos comportamientos automáticos.
* Aplicar la **comunicación entre procesos** con `mpi4py`.
* Estudiar cómo se puede estructurar una aplicación distribuida en Python.
* Medir y comparar el rendimiento de estrategias automáticas.
* Analizar estadísticas de juego: precisión, duración, aciertos, etc.

Este proyecto tiene un valor educativo y experimental, siendo ideal para practicar la programación concurrente y los fundamentos de la paralelización en sistemas distribuidos.

---

## 🧩 2. Estructura del proyecto

El proyecto está organizado de forma modular para separar claramente las responsabilidades de cada componente. A continuación se describen los principales módulos y su función dentro del sistema:

### 🗂️ Archivos principales

| Archivo / Carpeta | Descripción                                                                             |
| ----------------- | --------------------------------------------------------------------------------------- |
| `main.py`         | Punto de entrada. Ejecuta simulaciones entre estrategias usando MPI.                    |
| `partida.py`      | Controla el desarrollo de una partida: turnos, intercambio de mensajes, y estadísticas. |
| `jugador.py`      | Define la clase `Jugador`, que gestiona el tablero propio y registra impactos.          |
| `flota.py`        | Genera flotas de barcos aleatorias en el tablero, asegurando reglas de colocación.      |
| `tablero.py`      | Funciones de visualización y registro de eventos de los tableros.                       |
| `constantes.py`   | Define constantes globales (símbolos, tamaño de tablero, número de partidas, etc.).     |
| `estrategias/`    | Carpeta con las estrategias implementadas (`aleatoria`, `optimizada`, `optimizada2`).   |
| `base.py`         | Clase base `EstrategiaDisparo` que define la interfaz común para todas las estrategias. |

### 🧠 Lógica modular

* Cada jugador es una instancia del proceso MPI, por lo que el código se ejecuta en paralelo desde el inicio.
* Las estrategias son clases intercambiables que encapsulan el comportamiento de disparo del jugador.
* Los tableros se actualizan y mantienen por separado en cada proceso, pero el resultado de los disparos se comunica de forma síncrona.

### 🔁 Flujo general

1. `main.py` ejecuta múltiples simulaciones entre todas las combinaciones posibles de estrategias.
2. En cada simulación, `partida.py` inicia una partida entre dos jugadores (`rank 0` y `rank 1`).
3. Cada jugador usa una estrategia distinta y se comunica con el oponente mediante `send/recv` de `mpi4py`.
4. Se recopilan estadísticas por partida, y al final se imprime un resumen global y una tabla de calor con los resultados.

Este diseño modular permite mantener una clara separación entre la lógica del juego, la estrategia de disparo y la infraestructura paralela.

---

## 🔄 3. Lógica paralela: turnos y comunicación

El núcleo del proyecto consiste en simular partidas del juego “Hundir la flota” entre dos jugadores distribuidos en **procesos paralelos** usando **MPI (Message Passing Interface)**, gestionado con la librería `mpi4py`.

### 🧠 Asignación de procesos

* Se utilizan exactamente **dos procesos MPI**:

  * `rank 0`: jugador 0
  * `rank 1`: jugador 1
* Cada proceso mantiene su **propio tablero**, **flota** y **estado interno** de la partida.

### ⏱️ Alternancia de turnos

La partida se organiza en turnos numerados:

* Si el número de turno es **par**, le toca disparar al `rank 0` (jugador 0).
* Si es **impar**, dispara el `rank 1` (jugador 1).

Cada jugador realiza un disparo en su turno y espera respuesta del otro proceso.

### 📤 Comunicación entre procesos

Se usa comunicación punto a punto con `send` y `recv` entre los dos procesos:

#### 🔫 Durante el turno de disparo:

1. El jugador que dispara calcula la coordenada `(x, y)` con su estrategia.
2. Envía la coordenada al oponente con `comm.send((x, y), dest=otro_rank, tag=0)`.
3. Espera la respuesta: `comm.recv(source=otro_rank, tag=1)`, que indica si fue “agua”, “tocado”, “hundido” o “FIN”.

#### 🛡️ Durante el turno de recibir disparo:

1. El proceso receptor recibe la coordenada.
2. Procesa el disparo sobre su tablero (`jugador.recibir_disparo(x, y)`).
3. Devuelve la respuesta al atacante con `comm.send(respuesta, dest=otro_rank, tag=1)`.

### 🏁 Fin del juego

* Si tras recibir un disparo, un jugador detecta que **todos sus barcos han sido hundidos**, devuelve el mensaje `"FIN"`.
* El otro jugador, al recibir `"FIN"`, termina también su ejecución.
* Ambos procesos finalizan la partida de forma sincronizada.

### 💬 Ventajas del modelo

* Simula correctamente la **interacción entre procesos distribuidos**, como en sistemas de múltiples nodos reales.
* Permite observar el comportamiento asíncrono del intercambio de mensajes.
* Sirve como base para desarrollar inteligencia artificial distribuida o juegos en red.

---

## 🎯 4. Estrategias de disparo implementadas

Las estrategias son el corazón del comportamiento de cada jugador. Cada estrategia implementa una forma distinta de decidir la próxima coordenada donde disparar.

Todas las estrategias heredan de la clase base `Estrategia`, ubicada en `estrategias/base.py`, y deben implementar el método:

```python
def siguiente_disparo(self) -> tuple[int, int]
```

### 📁 Estructura del módulo de estrategias

Cada estrategia se define como un módulo independiente en la carpeta `estrategias/`. Los nombres de las clases coinciden con el nombre del archivo:

* `aleatoria.py`
* `optimizada.py`
* `optimizada2.py`

Todas las estrategias verifican que la coordenada no haya sido disparada antes ni esté fuera de los límites del tablero.

---

### 🧩 Estrategia 1: `Aleatoria`

📄 Archivo: `estrategias/aleatoria.py`

* Selecciona **coordenadas aleatorias** que no haya repetido.
* No tiene memoria, no adapta su comportamiento.
* Se considera la más básica.

**Modo de funcionamiento:**

```python
(x, y) = random.choice(coordenadas_libres)
```

---

### 🎯 Estrategia 2: `Optimizada`

📄 Archivo: `estrategias/optimizada.py`

* Combina dos modos: `exploración` y `caza`.
* **Exploración**: dispara aleatoriamente.
* **Caza**: tras un impacto, busca a su alrededor inteligentemente hasta hundir el barco.

Mejora significativamente la eficiencia frente a estrategias aleatorias a la hora de hundir los barcos encontrados.

---

### 🧠 Estrategia 3: `Optimizada2`

📄 Archivo: `estrategias/optimizada2.py`

* Es una mejora sobre `optimizada`.
* Durante la exploración, dispara en un patrón de ajedrez, saltando más casillas.
* También evita zonas cercanas a barcos ya hundidos, expandiendo esa zona a una “burbuja” de seguridad, pues no se pueden colocar barcos adyacentes.

Mejora la eficiencia a la hora de encontrar barcos respecto a la primera estrategia optimizada.

---

## 🧱 5. Estructura del código y módulos principales

El proyecto está organizado en módulos funcionales, cada uno con una responsabilidad clara. A continuación se describe cada uno y su papel en la ejecución del programa.

---

### 📁 Estructura general

```
.
├── main.py                # Entrada principal del programa
├── partida.py             # Lógica del juego y comunicación MPI
├── jugador.py             # Clase Jugador (estrategia, tablero, flota)
├── flota.py               # Lógica de generación y manipulación de flotas
├── tablero.py             # Funciones auxiliares para imprimir y gestionar el tablero
├── constantes.py          # Parámetros globales (dimensiones, símbolos, etc.)
└── estrategias/
    ├── base.py            # Clase base común para todas las estrategias
    ├── aleatoria.py       # Estrategia aleatoria
    ├── optimizada.py      # Estrategia optimizada (modo caza/exploración)
    └── optimizada2.py     # Estrategia aún más precisa y eficiente
```

---

### 🧠 Módulos clave

#### `main.py`

* Lanza las partidas entre todas las combinaciones posibles de estrategias.
* Recoge las estadísticas globales.
* Imprime el resumen final y genera la matriz de enfrentamientos.
* Solo el **rank 0** realiza las impresiones y recogida de resultados globales.

---

#### `partida.py`

* Controla el desarrollo de una partida individual.
* Cada jugador se ejecuta en su propio proceso MPI.
* Implementa el bucle de turnos y la lógica de envío/recepción de disparos mediante `MPI.send` y `MPI.recv`.
* Registra eventos relevantes para posterior visualización.
* Retorna estadísticas detalladas de la partida.

---

#### `jugador.py`

* Define la clase `Jugador`, que agrupa:

  * La estrategia de disparo.
  * El tablero personal.
  * La flota de barcos y su estado.
* Se encarga de:

  * Procesar disparos recibidos.
  * Informar si ha perdido.
  * Delegar en la estrategia el siguiente disparo.

---

#### `flota.py`

* Lógica de generación de flotas aleatorias.
* Asegura que los barcos:

  * No se solapen.
  * Estén dentro del tablero.
  * No estén adyacentes ni en diagonal entre sí.
* También permite transformar coordenadas de flotas y aplicar máscaras de distancia.

---

#### `tablero.py`

* Utilidades para imprimir tableros en consola:

  * En cada turno relevante.
  * Al final de la partida.
* Se adapta para ocultar barcos cuando sea necesario.

---

#### `constantes.py`

* Define:

  * Dimensiones del tablero (`BOARD_SIZE`).
  * Símbolos para agua, barco, tocado (`O`, `B`, `X`).
  * Número de simulaciones (`NUM_SIMULACIONES`).
* Cualquier modificación de parámetros debe hacerse aquí.

---

#### `estrategias/`

* Carpeta que contiene las distintas estrategias de disparo.
* Cada estrategia hereda de `EstrategiaBase` y define su comportamiento en `siguiente_disparo`.

---

## 📊 6. Visualización y Análisis de Resultados

Para evaluar el rendimiento de cada estrategia, se realizaron **50.000 partidas** por cada posible combinación de estrategias, donde una actuaba como Jugador 0 y otra como Jugador 1. Se recopilaron métricas clave como:

* Número de victorias para cada jugador.
* Porcentaje de precisión (aciertos/disparos).
* Número promedio de disparos por partida.
* Duración promedio por partida (en segundos).
* Número promedio de turnos por enfrentamiento.

Estas métricas permiten una evaluación cuantitativa del rendimiento relativo entre estrategias.

### Tabla resumen por enfrentamiento

La siguiente tabla resume los resultados agregados de cada combinación, mostrando para cada pareja:

* Victorias absolutas y relativas de J0 y J1.
* Precisión media de disparos.
* Turnos y duración promedio.

| Jugador 0   | Jugador 1   | J0 gana | J1 gana | % J0   | % J1   | Turnos | Precisión J0 | Precisión J1 | Disparos J0 | Disparos J1 |
| ----------- | ----------- | ------- | ------- | ------ | ------ | ------ | ------------ | ------------ | ----------- | ----------- |
| Aleatoria   | Aleatoria   | 25611   | 24389   | 51.2%  | 48.8%  | 735.5  | 4.2%         | 4.2%         | 368.0       | 367.5       |
| Aleatoria   | Optimizada  | 420     | 49580   | 0.8%   | 99.2%  | 423.5  | 4.3%         | 7.6%         | 211.8       | 211.7       |
| Aleatoria   | Optimizada 2| 1       | 49999   | 0.0%   | 100.0% | 309.3  | 4.2%         | 10.3%        | 154.6       | 154.6       |
| Optimizada  | Aleatoria   | 49534   | 466     | 99.1%  | 0.9%   | 424.1  | 7.5%         | 4.2%         | 212.5       | 211.5       |
| Optimizada  | Optimizada  | 24924   | 25076   | 49.8%  | 50.2%  | 347.3  | 8.2%         | 8.2%         | 173.9       | 173.4       |
| Optimizada  | Optimizada 2| 12015   | 37985   | 24.0%  | 76.0%  | 291.0  | 8.9%         | 10.4%        | 145.6       | 145.4       |
| Optimizada 2| Aleatoria   | 50000   | 0       | 100.0% | 0.0%   | 307.7  | 10.4%        | 4.2%         | 154.3       | 153.3       |
| Optimizada 2| Optimizada  | 38364   | 11636   | 76.7%  | 23.3%  | 290.1  | 10.4%        | 8.9%         | 145.4       | 144.7       |
| Optimizada 2| Optimizada 2| 25350   | 24650   | 50.7%  | 49.3%  | 272.5  | 10.5%        | 10.5%        | 136.5       | 136.0       |


### Mapa de calor de victorias del Jugador 1

Esta tabla muestra el porcentaje de victorias del Jugador 1 para cada combinación:

| J0 \ J1         | Aleatoria | Optimizada | Optimizada 2|
| --------------- | --------- | ---------- | ----------- |
| **Aleatoria**   | 48.8%     | 99.2%      | 100.0%      |
| **Optimizada**  | 0.9%      | 50.2%      | 76.0%       |
| **Optimizada 2**| 0.0%      | 23.3%      | 49.3%       |

Estos datos indican un claro crecimiento en efectividad de las estrategias más avanzadas como `optimizada2`, que domina casi todas las combinaciones excepto contra sí misma, donde mantiene un equilibrio.

---

## 🛠️ 7. Ejecución y configuración del proyecto

Este proyecto está diseñado para ejecutarse en un entorno de **computación paralela con MPI (Message Passing Interface)**. Cada partida se ejecuta en dos procesos, uno por jugador. A continuación se explican los pasos necesarios para compilar, ejecutar y personalizar el experimento.

### 7.1 Requisitos

* Python 3.7 o superior

* `mpi4py` instalado:

  ```bash
  pip install mpi4py
  ```

* Un entorno compatible con MPI, como:

  * OpenMPI (`mpiexec`, `mpirun`)
  * Intel MPI
  * MPICH

---

### 7.2 Ejecutar simulaciones

Para lanzar la simulación de partidas entre todas las combinaciones de estrategias, usaremos:

```bash
mpiexec -n 2 python main.py
```

Este comando lanza dos procesos paralelos que ejecutarán partidas por turnos entre dos jugadores. Se repetirán automáticamente todas las combinaciones de estrategias definidas.

---

### 7.3 Configurar parámetros del experimento

El archivo `constantes.py` contiene todas las configuraciones principales del juego. Se puede ajustar:

```python
# constantes.py

NUM_SIMULACIONES = 100  # Número de partidas por combinación
BOARD_SIZE = 10         # Tamaño del tablero (NxN)
MOSTRAR_TABLERO = False # Mostrar evolución del tablero por consola
```

Se puede aumentar `NUM_SIMULACIONES` para mayor precisión estadística (por ejemplo, 50000), o activar `MOSTRAR_TABLERO` para imprimir los tableros para una depuración visual.

---

### 7.4 Añadir nuevas estrategias

Para probar nuevas estrategias, simplemente se pueden crear en un nuevo archivo en `estrategias/` heredando de `BaseEstrategia`:

```python
from estrategias.base import BaseEstrategia

class MiEstrategia(BaseEstrategia):
    def siguiente_disparo(self):
        # lógica del disparo
        pass
```

Luego, basta con registras esta estrategia en el diccionario `ESTRATEGIAS_DISPONIBLES` dentro de `partida.py`.

---

## 8. Conclusión

Este proyecto ha servido como una demostración práctica del uso de **MPI** en Python para computación paralela basada en procesos. Se ha modelado un entorno competitivo, donde distintas estrategias autónomas compiten en una partida de **batalla naval**. Gracias al uso de `mpi4py`, cada jugador funciona de forma independiente, sincronizándose solo para intercambiar disparos y registrar resultados.

La estructura modular permite **fácil extensibilidad**, tanto en estrategias como en visualización, y se ha verificado el impacto significativo de estrategias optimizadas en entornos simulados masivos.
