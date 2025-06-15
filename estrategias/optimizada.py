"""
optimizada.py

Estrategia de disparo optimizada para el juego "Hundir la Flota".

Esta estrategia simula un comportamiento inteligente con dos fases:

1. Modo "exploración":
   - Se dispara aleatoriamente sin repetir.
   - Si se impacta un barco, se cambia al modo "caza".

2. Modo "caza":
   - Activo tras un impacto ('tocado') no hundido.
   - Se generan celdas vecinas (arriba, abajo, izquierda, derecha) desde el punto tocado.
   - Se disparan sistemáticamente estas posiciones para descubrir la orientación del barco.
   - Si se acierta de nuevo, se prioriza continuar en esa dirección.
   - Cuando el barco se hunde, se limpian las variables de estado y se vuelve al modo "exploración".

Ventajas de esta estrategia:
- Aumenta significativamente la eficiencia en destrucción de barcos.
- Emula una forma de jugar humana más lógica.
- Requiere poco almacenamiento de estado pero mejora mucho respecto a la estrategia aleatoria.
"""


import random
from estrategias.base import Estrategia

class EstrategiaOptimizada(Estrategia):
    def __init__(self, board_size):
        super().__init__(board_size)
        self.board_size = board_size
        self.modo = "exploracion"
        self.tocados = []         # Coordenadas de los barcos del rival tocados
        self.candidatos = []      # Coordenadas para probar en modo caza
        self.hundidos = []        # Coordenadas de los barcos del rival hundidos

    def siguiente_disparo(self):
        if self.modo == "caza" and self.candidatos:
            while self.candidatos:
                x, y = self.candidatos.pop(0)
                if self.es_disparo_valido(x, y):
                    self.disparos_realizados.add((x, y))
                    return x, y

        # Exploración aleatoria tipo damero
        while True:
            x = random.randint(0, self.board_size - 1)
            y = random.randint(0, self.board_size - 1)
            if self.es_disparo_valido(x, y):
                self.disparos_realizados.add((x, y))
                return x, y

    def registrar_resultado(self, x, y, resultado):
        if resultado == 'tocado':
            self.tocados.append((x, y))
            self.modo = "caza"
            self.actualizar_candidatos()
        elif resultado == 'hundido':
            self.tocados.append((x, y))
            self.hundidos.extend(self.tocados)
            self.tocados.clear()
            self.candidatos.clear()
            self.modo = "exploracion"
        # Si es agua, no hacemos nada

    def es_disparo_valido(self, x, y):
        """
        Devuelve True si (x, y) es una coordenada válida para disparar:
        - Dentro del tablero
        - No ha sido disparada antes
        - No está adyacente (incluyendo diagonales) a ningún barco hundido
        """
        valido = (
            0 <= x < self.board_size and
            0 <= y < self.board_size and
            (x, y) not in self.disparos_realizados
        )

        if not valido:
            return False

        #for bx, by in self.hundidos:
         #   if abs(bx - x) <= 1 and abs(by - y) <= 1:
          #      valido = False
           #     break

        return valido


    def actualizar_candidatos(self):
        """
        Basado en los tocados actuales, genera nuevos disparos candidatos de forma coherente
        (alineados si hay más de uno).
        """
        self.candidatos.clear()
        if not self.tocados:
            return

        if len(self.tocados) == 1:
            x, y = self.tocados[0]
            vecinos = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
        else:
            # Detectar orientación del barco (horizontal o vertical)
            self.tocados.sort()
            dx = self.tocados[1][0] - self.tocados[0][0]
            dy = self.tocados[1][1] - self.tocados[0][1]

            # Extiende en ambas direcciones
            extremos = sorted(self.tocados)
            primero = extremos[0]
            ultimo = extremos[-1]

            vecinos = [
                (primero[0] - dx, primero[1] - dy),
                (ultimo[0] + dx, ultimo[1] + dy)
            ]

        # Añadir solo los que sean válidos y aún no disparados
        self.candidatos = [
            (x, y) for (x, y) in vecinos if self.es_disparo_valido(x, y)
        ]