"""
flota.py

Este módulo contiene funciones relacionadas con la gestión de la flota de barcos.

Responsabilidades principales:
- Generar una flota de barcos con tamaños específicos.
- Colocar los barcos en un tablero de forma aleatoria, evitando solapamientos y
  asegurando que estén dentro de los límites del tablero.

Cada barco se representa como una lista de coordenadas (x, y), y la flota es una
lista de estos barcos.

Dependencias:
- constantes.py: proporciona valores como el tamaño del tablero y símbolos del juego.
"""

import random
from constantes import BOARD_SIZE, SIMBOLO_BARCO, SIMBOLO_VACIO

def generar_flota(tablero, tamanos_barcos):
    """
    Genera y coloca una flota de barcos en el tablero dado, asegurando que
    haya al menos una casilla de separación (incluso diagonal) entre barcos.

    Args:
        tablero: matriz 2D que representa el tablero del jugador.
        tamanos_barcos: lista con los tamaños de cada barco (ej: [5,4,3,3,2]).

    Returns:
        flota: lista de barcos, donde cada barco es una lista de coordenadas (x, y).
    """
    flota = []

    def area_adyacente_libre(coords):
        for x, y in coords:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
                        if tablero[nx][ny] == SIMBOLO_BARCO:
                            return False
        return True

    for tam in tamanos_barcos:
        colocado = False

        while not colocado:
            orientacion = random.choice(['H', 'V'])

            if orientacion == 'H':
                x = random.randint(0, BOARD_SIZE - 1)
                y = random.randint(0, BOARD_SIZE - tam)
                coords = [(x, y + i) for i in range(tam)]
            else:
                x = random.randint(0, BOARD_SIZE - tam)
                y = random.randint(0, BOARD_SIZE - 1)
                coords = [(x + i, y) for i in range(tam)]

            # Verifica que las casillas y las adyacentes estén libres
            if all(tablero[xi][yi] == SIMBOLO_VACIO for xi, yi in coords) and area_adyacente_libre(coords):
                for xi, yi in coords:
                    tablero[xi][yi] = SIMBOLO_BARCO
                flota.append(coords)
                colocado = True

    return flota
