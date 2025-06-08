"""
tablero.py

Este módulo gestiona el tablero del juego "Hundir la Flota".

Contiene funciones para:
- Crear un tablero vacío.
- Marcar disparos.
- Imprimir el tablero en consola en modo texto (compatible con cualquier terminal).
"""

from constantes import BOARD_SIZE, SIMBOLO_VACIO, SIMBOLO_BARCO
import os
import platform

def crear_tablero():
    """
    Crea y devuelve un tablero vacío.
    """
    return [[SIMBOLO_VACIO for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

def marcar_disparo(tablero, x, y, simbolo):
    """
    Marca un disparo en el tablero.
    """
    tablero[x][y] = simbolo

def limpiar_consola():
    """
    Limpia la consola del sistema actual.
    """
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def imprimir_tablero(tablero, mostrar_barcos=True, jugador_id=None):
    """
    Imprime el tablero en consola en modo texto simple.

    Parámetros:
        tablero: matriz del tablero del jugador.
        mostrar_barcos: si False, oculta los barcos.
        jugador_id: número del jugador (opcional).
    """
    limpiar_consola()

    titulo = f"  === TABLERO DEL JUGADOR {jugador_id} ===" if jugador_id is not None else "  === TABLERO ==="
    print(titulo)

    # Encabezado columnas
    cabecera = "    " + " ".join([f"{i:2}" for i in range(BOARD_SIZE)])
    print(cabecera)

    for i, fila in enumerate(tablero):
        fila_str = f"{i:2} |"
        for celda in fila:
            if celda == SIMBOLO_BARCO and not mostrar_barcos:
                fila_str += "   "
            else:
                fila_str += f" {celda} "
        print(fila_str)
