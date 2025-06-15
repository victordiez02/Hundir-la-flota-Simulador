"""
base.py

Define la clase base que todas las estrategias deben heredar.
"""

from abc import ABC, abstractmethod

class Estrategia(ABC):
    def __init__(self, board_size):
        self.board_size = board_size
        self.disparos_realizados = set()

    @abstractmethod
    def siguiente_disparo(self):
        """
        Devuelve una tupla (x, y) con la próxima coordenada a disparar.
        """
        pass

    @abstractmethod
    def registrar_resultado(self, x, y, resultado):
        """
        Informa del resultado ('agua', 'tocado', 'hundido') del último disparo.
        """
        pass
