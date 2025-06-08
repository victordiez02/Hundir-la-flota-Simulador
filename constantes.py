"""
constantes.py

Contiene todas las constantes globales del juego "Hundir la Flota".

Estas constantes se utilizan en la creación del tablero, colocación de la flota
y visualización del estado del juego. Están separadas para facilitar su modificación
y mantener una configuración centralizada.
"""

from estrategias.aleatoria import EstrategiaAleatoria
from estrategias.optimizada import EstrategiaOptimizada
from estrategias.optimizada2 import EstrategiaOptimizada2

# === Parámetros generales ===

# Tamaño del tablero (cuadrado)
BOARD_SIZE = 20

# Número de simulaciones a realizar en una partida por estrategia
NUM_SIMULACIONES = 1

# Estrategias disponibles
ESTRATEGIAS_DISPONIBLES = {
    "optimizada2": EstrategiaOptimizada2,
}

# Activa o desactiva impresión en tiempo real
MOSTRAR_DISPAROS = "Solo aciertos"  
# Opciones: "Todos", "Solo aciertos", "Ninguno"

MOSTRAR_TABLERO = True
# (True para ver el tablero en cada turno, False para no mostrarlo)
# Está desactivado por defecto para evitar saturar la salida en MPI.
# Solo está para debugging o pruebas locales.  

# Tamaños de los barcos en la flota
# (5 barcos: 1 de tamaño 5, 1 de tamaño 4, 2 de tamaño 3, 1 de tamaño 2)
TAMANOS_BARCOS = [5, 4, 3, 3, 2]

# Caracteres utilizados para representar los diferentes estados del tablero
SIMBOLO_VACIO = ' '
SIMBOLO_BARCO = 'B'
SIMBOLO_AGUA = 'O'
SIMBOLO_TOCADO = 'X'
