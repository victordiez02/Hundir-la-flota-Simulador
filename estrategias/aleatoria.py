"""
aleatoria.py

Estrategia que dispara completamente al azar en posiciones no repetidas.
"""

import random
from estrategias.base import Estrategia

class EstrategiaAleatoria(Estrategia):
    def siguiente_disparo(self):
        while True:
            x = random.randint(0, self.board_size - 1)
            y = random.randint(0, self.board_size - 1)
            if (x, y) not in self.disparos_realizados:
                self.disparos_realizados.add((x, y))
                return x, y

    def registrar_resultado(self, x, y, resultado):
        # Esta estrategia no reacciona al resultado, solo lo guarda.
        pass
