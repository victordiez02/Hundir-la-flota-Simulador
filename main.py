"""
main.py

Ejecuta simulaciones entre todas las combinaciones posibles de estrategias dos a dos.
"""

from mpi4py import MPI
import numpy as np
from rich.table import Table
from rich.console import Console
from partida import jugar_una_partida, ESTRATEGIAS_DISPONIBLES
from constantes import NUM_SIMULACIONES

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    if size < 3:
        if rank == 0:
            print("Este programa requiere al menos 3 procesos MPI (2 jugadores + 1 coordinador).")
        return

    estrategias = list(ESTRATEGIAS_DISPONIBLES.keys())

    if rank == 2:
        resultados = []
        # Proceso maestro: gestiona todas las combinaciones de estrategias y controla los turnos
        for e0 in estrategias:
            for e1 in estrategias:
                print(f"\nSimulando {NUM_SIMULACIONES} partidas entre {e0.upper()} vs {e1.upper()}...\n")
                for _ in range(NUM_SIMULACIONES):
                    # En cada partida, se envían las estrategias a rank 0 y 1
                    comm.send((e0, e1), dest=0, tag=0)
                    comm.send((e0, e1), dest=1, tag=0)

                    # Recogemos los resultados desde el rank 0
                    resultado = comm.recv(source=0, tag=1)
                    resultados.append(resultado)
        # Después de todas las partidas, se manda una señal de parada
        comm.send(None, dest=0, tag=9)
        comm.send(None, dest=1, tag=9)

        # STATS FINALES DE LAS PARTIDAS (las imprime el rank 2)
        resumen = {}
        for r in resultados:
            clave = (r["estrategia_j0"], r["estrategia_j1"])
            if clave not in resumen:
                resumen[clave] = {
                    "j0_gana": 0,
                    "j1_gana": 0,
                    "turnos": [],
                    "duraciones": [],
                    "disparos_j0": [],
                    "disparos_j1": [],
                    "aciertos_j0": [],
                    "aciertos_j1": [],
                }

            resumen[clave]["turnos"].append(r["turnos"])
            resumen[clave]["duraciones"].append(r["duracion"])
            resumen[clave]["disparos_j0"].append(r["disparos_j0"])
            resumen[clave]["disparos_j1"].append(r["disparos_j1"])
            resumen[clave]["aciertos_j0"].append(r["aciertos_j0"])
            resumen[clave]["aciertos_j1"].append(r["aciertos_j1"])

            if r["ganador"] == 0:
                resumen[clave]["j0_gana"] += 1
            else:
                resumen[clave]["j1_gana"] += 1

        print("\n=== RESUMEN COMBINACIONES ===")
        estrategias_set = list(set([r["estrategia_j0"] for r in resultados]))
        estrategias_set.sort()
        matriz = np.zeros((len(estrategias_set), len(estrategias_set)))  # filas: j0, columnas: j1

        for (e0, e1), data in resumen.items():
            total = data["j0_gana"] + data["j1_gana"]
            idx0 = estrategias_set.index(e0)
            idx1 = estrategias_set.index(e1)
            pct_j1 = (data["j1_gana"] / total) * 100 if total else 0
            matriz[idx0][idx1] = pct_j1

            # También imprime resumen por combinación
            prom_turnos = sum(data["turnos"]) / total
            prom_duracion = sum(data["duraciones"]) / total
            prom_disparos_j0 = sum(data["disparos_j0"]) / total
            prom_disparos_j1 = sum(data["disparos_j1"]) / total
            prom_aciertos_j0 = sum(data["aciertos_j0"]) / total
            prom_aciertos_j1 = sum(data["aciertos_j1"]) / total
            prec_j0 = (prom_aciertos_j0 / prom_disparos_j0) * 100 if prom_disparos_j0 else 0
            prec_j1 = (prom_aciertos_j1 / prom_disparos_j1) * 100 if prom_disparos_j1 else 0

            print(f"{e0} vs {e1}:")
            print(f"  - J0 gana {data['j0_gana']}/{total},  J1 gana {data['j1_gana']}/{total}")
            print(f"  - Prom. turnos: {prom_turnos:.1f}")
            print(f"  - Prom. duracion: {prom_duracion:.2f}s")
            print(f"  - Precision J0: {prec_j0:.1f}%,  Precision J1: {prec_j1:.1f}%")
            print(f"  - Disparos por partida: J0={prom_disparos_j0:.1f}, J1={prom_disparos_j1:.1f}")
            print()

        # === IMPRESIÓN DE TABLA DE PORCENTAJES DE VICTORIA DE J1 ===
        console = Console()
        table = Table(title="Porcentaje de victorias del Jugador 1", show_lines=True)
        table.add_column("J0 \\ J1", justify="right")

        for nombre in estrategias_set:
            table.add_column(nombre, justify="center")

        for i, e0 in enumerate(estrategias_set):
            fila = [e0] + [f"{matriz[i][j]:.1f}%" for j in range(len(estrategias_set))]
            table.add_row(*fila)

        if NUM_SIMULACIONES >1: console.print(table)
        
    else:
        # Jugadores: ejecutan partidas cuando reciben estrategias del coordinador
        while True:
            status = MPI.Status()
            datos = comm.recv(source=2, tag=MPI.ANY_TAG, status=status)
            if status.Get_tag() == 9:
                break
            e0, e1 = datos
            resultado = jugar_una_partida(e0, e1)
            if rank == 0:
                comm.send(resultado, dest=2, tag=1)


if __name__ == "__main__":
    main()
