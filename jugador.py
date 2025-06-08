"""
jugador.py

Este módulo define la clase Jugador para el juego "Hundir la Flota" distribuido
con MPI. Cada jugador mantiene su propio estado (tablero, flota, estrategia)
y es responsable de:

- Elegir dónde disparar (usando una estrategia concreta).
- Registrar el resultado de sus disparos.
- Procesar los disparos que recibe del oponente.
- Determinar si ha perdido la partida (flota destruida).

La clase está diseñada para funcionar en un entorno de memoria distribuida, es decir,
cada proceso MPI mantiene su propia instancia de Jugador, sin memoria compartida.
"""

from tablero import crear_tablero, marcar_disparo
from flota import generar_flota
from constantes import TAMANOS_BARCOS, SIMBOLO_TOCADO, SIMBOLO_AGUA
from estrategias.base import Estrategia

class Jugador:
    def __init__(self, estrategia: Estrategia, board_size: int):
        """
        Inicializa un jugador con una estrategia de disparo y tablero vacío.

        Parámetros:
            estrategia: instancia de una clase que hereda de Estrategia.
            board_size: tamaño del tablero (e.g., 20).
        """
        self.board_size = board_size
        self.estrategia = estrategia
        self.tablero = crear_tablero()
        self.flota = generar_flota(self.tablero, TAMANOS_BARCOS)

    def siguiente_disparo(self):
        """
        Obtiene la siguiente coordenada a disparar, delegando en la estrategia.

        Retorna:
            (x, y): coordenadas del disparo.
        """
        return self.estrategia.siguiente_disparo()

    def registrar_resultado_disparo(self, x, y, resultado):
        """
        Informa a la estrategia del resultado del disparo más reciente.

        Parámetros:
            x, y: coordenadas disparadas.
            resultado: 'agua', 'tocado' o 'hundido'.
        """
        self.estrategia.registrar_resultado(x, y, resultado)

    def recibir_disparo(self, x, y):
        """
        Procesa un disparo que el oponente ha lanzado contra este jugador.

        Actualiza el tablero y flota, y determina el resultado del impacto.

        Parámetros:
            x, y: coordenadas del disparo recibido.

        Retorna:
            resultado: 'agua', 'tocado', 'hundido' o 'FIN' si el jugador ha perdido.
        """
        for barco in self.flota:
            if (x, y) in barco:
                marcar_disparo(self.tablero, x, y, SIMBOLO_TOCADO)
                barco.remove((x, y))
                if not barco:
                    self.flota.remove(barco)
                    if not self.flota:
                        return "FIN"  # Toda la flota destruida
                    return 'hundido'
                else:
                    return 'tocado'

        # Si no impacta ningún barco
        marcar_disparo(self.tablero, x, y, SIMBOLO_AGUA)
        return 'agua'
