"""
partida.py

Este módulo implementa la lógica central del juego "Hundir la Flota" distribuido con MPI.

Se utilizan dos procesos (rank 0 y rank 1), cada uno con su propia instancia de Jugador
y estrategia de disparo. La comunicación se realiza de forma explícita mediante MPI_Send
y MPI_Recv, alternando turnos hasta que un jugador pierde toda su flota.

Funciones:
- jugar_una_partida(): ejecuta una única partida y devuelve estadísticas de la misma.
"""

from mpi4py import MPI
from jugador import Jugador
from constantes import BOARD_SIZE, ESTRATEGIAS_DISPONIBLES, MOSTRAR_TABLERO, MOSTRAR_DISPAROS

import time


# Lista de eventos que se imprimirán al final
eventos_tablero = []

def guardar_tablero_evento(eventos_tablero, jugador_id, atacante_id, turno, coordenadas, tablero, resultado):
    """
    Guarda un evento relevante del juego para ser impreso después.

    Args:
        jugador_id: jugador que recibe el disparo.
        atacante_id: jugador que ha disparado.
        turno: número de turno.
        tablero: estado del tablero del jugador receptor.
        resultado: resultado del disparo ("agua", "tocado", "hundido", "FIN").
    """
    evento = {
        "turno": turno,
        "atacante": atacante_id,
        "receptor": jugador_id,
        "coordenadas": coordenadas,
        "resultado": resultado
    }

    if MOSTRAR_TABLERO:
        evento["tablero"] = [row[:] for row in tablero]  # Copia profunda de las filas

    eventos_tablero.append(evento)

def imprimir_eventos_guardados(eventos_tablero, mostrar_tablero=False):
    """
    Imprime todos los eventos de tablero guardados tras la partida, en orden cronológico,
    con información del disparo, modo, proceso y si se ha hundido un barco.
    """
    for evento in sorted(eventos_tablero, key=lambda x: x['turno']):
        turno = evento['turno']
        atacante = evento['atacante']
        receptor = evento['receptor']
        coordenadas = evento['coordenadas']
        if mostrar_tablero: tablero = evento['tablero']
        resultado = evento['resultado']

        print("\n" + "=" * 60)
        print(f"[ Turno {turno} ]")
        print(f" -> Jugador {atacante} ha disparado en {coordenadas} al Jugador {receptor}.")
        if resultado == 'tocado':
            print(f" -> [TOCADO]")
        elif resultado == 'hundido':
            print(f" -> [HUNDIDO]")
        elif resultado == 'agua':
            print(f" -> [AGUA]")

        # Encabezado columnas
        if mostrar_tablero:
            print(f" -> Tablero del Jugador {receptor} tras recibir el disparo.")
            titulo = f"  === TABLERO DEL JUGADOR {receptor} ==="
            print(titulo)
            cabecera = "    " + " ".join([f"{i:2}" for i in range(BOARD_SIZE)])
            print(cabecera)

            for i, fila in enumerate(tablero):
                fila_str = f"{i:2} |"
                for celda in fila:
                    fila_str += f" {celda} "
                print(fila_str)

def jugar_una_partida(nombre_estrategia_0, nombre_estrategia_1):
    """
    Ejecuta una partida entre dos procesos MPI y devuelve estadísticas.

    Parámetros:
        nombre_estrategia_0 (str): nombre de la estrategia para el jugador 0.
        nombre_estrategia_1 (str): nombre de la estrategia para el jugador 1.

    Retorna (solo en rank 0):
        dict con:
            - 'ganador': 0 o 1
            - 'turnos': número total de turnos jugados
            - 'disparos_j0': total disparos jugador 0
            - 'aciertos_j0': total impactos jugador 0
            - 'disparos_j1': total disparos jugador 1
            - 'aciertos_j1': total impactos jugador 1
            - 'estrategia_j0': nombre estrategia jugador 0
            - 'estrategia_j1': nombre estrategia jugador 1
            - 'duracion': duración de la partida en segundos
    """
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    assert size == 3, "Este juego requiere exactamente 3 procesos MPI."

    # === Instanciar jugador y estrategia ===
    estrategia_nombre = nombre_estrategia_0 if rank == 0 else nombre_estrategia_1
    estrategia_clase = ESTRATEGIAS_DISPONIBLES[estrategia_nombre]
    estrategia = estrategia_clase(board_size=BOARD_SIZE)
    jugador = Jugador(estrategia, board_size=BOARD_SIZE)

    # === Estadísticas locales ===
    # Solo el jugador rank 0 lleva el turno, para no desincronizar
    if rank == 0:
        turno = 0
        comm.send(turno, dest=1, tag=99)
    else:
        turno = comm.recv(source=0, tag=99)

    juego_terminado = False
    disparos_realizados = 0
    aciertos = 0
    inicio = time.time()
    # Inicialización para visualización
    caza = False  # Variable para indicar si se está cazando
    resultado_anterior = None
    ganador = None  # inicialización segura

    # === Bucle principal del juego ===
    while not juego_terminado:

        # === TURNO DE REALIZAR DISPARO ===
        if turno % 2 == rank:
            # Dispara el jugador que le toca y le manda las coordenadas al otro jugador
            x, y = jugador.siguiente_disparo()
            comm.send((x, y), dest=1 - rank, tag=0)

            # Recibimos la información del jugador que encaja el disparo y la registramos
            respuesta = comm.recv(source=1 - rank, tag=1)
            jugador.registrar_resultado_disparo(x, y, respuesta)

            disparos_realizados += 1 # para las estadísticas
            if respuesta in ['tocado', 'hundido']:
                aciertos += 1 # para las estadísticas

            # Terminamos el juego si el otro jugador nos indica que hemos
            # hundido su último barco
            if respuesta == "FIN":
                juego_terminado = True
                ganador = rank

        # === TURNO DE RECIBIR DISPARO ===
        else:
            # En el caso de recibir disparo, el jugador disparado recoge las coordenadas que
            # le manda el jugador atacante y responde si le ha sido agua, tocado, hundido
            # o FIN (si ha perdido toda su flota)
            x, y = comm.recv(source=1 - rank, tag=0)
            resultado = jugador.recibir_disparo(x, y)
            comm.send(resultado, dest=1 - rank, tag=1)

            # Comprobamos si el jugador que dispara ha dado a un barco para actualizar
            # estadísticas y ver si registramos el evento

            if estrategia_nombre == "optimizada":
                if resultado == 'tocado':
                    caza = True
                elif resultado == 'hundido':
                    caza = False
            match MOSTRAR_DISPAROS:
                case "Solo aciertos":
                    debe_guardar = (
                        turno < 2 or
                        resultado in {'tocado', 'hundido'} or
                        resultado_anterior == 'hundido' or
                        caza or
                        juego_terminado
                    )
                    resultado_anterior = resultado
                case "Todos":
                    debe_guardar = True
                case "Ninguno":
                    debe_guardar = True

            # Registramos si corresponde
            if debe_guardar:
                guardar_tablero_evento(
                        eventos_tablero = eventos_tablero,
                        jugador_id=1 - turno % 2,
                        atacante_id=turno % 2,
                        turno=turno,
                        coordenadas=(x, y),
                        tablero=jugador.tablero if MOSTRAR_TABLERO else None, # tablero del jugador que recibe el disparo
                        resultado=resultado
                    )

            if resultado == "FIN":
                juego_terminado = True

        # Actualizamos el turno: rank 0 incrementa el turno y lo envía a rank 1,
        # este lo recibe y lo actualiza
        if rank == 0:
            turno += 1
            comm.send(turno, dest=1, tag=99)
        else:
            turno = comm.recv(source=0, tag=99)

    # === Enviar / Recoger estadísticas ===
    fin = time.time()

    stats_locales = {
        "disparos": disparos_realizados,
        "aciertos": aciertos
    }

    # Enviamos las estadísticas y eventos de tabñer del jugador rank 1 al
    # jugador rank 0 para que las procese y las imprima
    if rank == 0:
        stats_remotas = comm.recv(source=1, tag=2)
        eventos_tablero_remoto = comm.recv(source=1, tag=3)

        # Recogemos los eventos del tablero del jugador remoto y la añadimos
        # a los eventos del tablero local 
        todos_los_eventos = eventos_tablero + eventos_tablero_remoto

        if MOSTRAR_DISPAROS != "Ninguno":
            if MOSTRAR_TABLERO:
                imprimir_eventos_guardados(todos_los_eventos, True)
            else:
                imprimir_eventos_guardados(todos_los_eventos, False)

        return {
            "ganador": ganador,
            "turnos": turno,
            "disparos_j0": stats_locales["disparos"],
            "aciertos_j0": stats_locales["aciertos"],
            "disparos_j1": stats_remotas["disparos"],
            "aciertos_j1": stats_remotas["aciertos"],
            "estrategia_j0": nombre_estrategia_0,
            "estrategia_j1": nombre_estrategia_1,
            "duracion": round(fin - inicio, 3),
        }

    else:
        comm.send(stats_locales, dest=0, tag=2)
        comm.send(eventos_tablero, dest=0, tag=3)
        return None

    
