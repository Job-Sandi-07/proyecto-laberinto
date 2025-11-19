import os
import sys
import random
import time
from typing import List

from src.mapa import generar_mapa
from src.jugador import Jugador
from src.entidades import Enemigo, MODO_ESCAPA, MODO_CAZADOR
from src.puntuacion import (
    calcular_puntaje_escapa,
    calcular_puntaje_cazador,
)


NUM_ENEMIGOS_INICIALES = 3


def limpiar_pantalla() -> None:
    # No es perfecto, pero funciona en la mayoría de casos
    os.system("cls" if os.name == "nt" else "clear")


def leer_entrada_usuario() -> str:
    comando = input("Mover (WASD), R=correr, Q=salir: ").strip().lower()
    return comando[:1] if comando else ""


def crear_enemigos_iniciales(mapa, cantidad: int) -> List[Enemigo]:
    enemigos: List[Enemigo] = []
    ancho = mapa.ancho
    alto = mapa.alto

    while len(enemigos) < cantidad:
        ex = random.randint(0, ancho - 1)
        ey = random.randint(0, alto - 1)

        # No ponerlos encima del jugador inicial ni de la salida
        if (ex, ey) == mapa.inicio_jugador or (ex, ey) == mapa.salida:
            continue

        # Solo en casillas transitables para enemigos
        if not mapa.es_transitable_por_enemigo(ex, ey):
            continue

        enemigos.append(Enemigo(ex, ey))

    return enemigos


# ======================================================
#                 MODO ESCAPA
# ======================================================

def jugar_modo_escapa() -> None:
    ancho = 20
    alto = 12

    mapa = generar_mapa(ancho, alto)
    inicio_x, inicio_y = mapa.inicio_jugador

    jugador = Jugador(x=inicio_x, y=inicio_y)

    # Crear enemigos iniciales para modo Escapa
    enemigos = crear_enemigos_iniciales(mapa, NUM_ENEMIGOS_INICIALES)

    tiempo_inicio = time.monotonic()

    while True:
        limpiar_pantalla()

        print("=== MODO ESCAPA ===")
        print(f"Inicio del jugador: {mapa.inicio_jugador}")
        print(f"Salida: {mapa.salida}")
        print(f"Enemigos en el mapa: {len([e for e in enemigos if e.vivo])}")
        print()

        posiciones_enemigos = [e.posicion for e in enemigos if e.vivo]

        # Mostrar mapa con el jugador y los enemigos
        mapa.mostrar_en_consola(
            pos_jugador=jugador.posicion(),
            posiciones_enemigos=posiciones_enemigos,
        )

        print()
        print("Energía:", jugador.obtener_barra_energia())
        print("(R para activar/desactivar correr)")
        print("Las 'E' son cazadores que te persiguen. Si te tocan, mueres.")
        print()

        # 1) Comprobar si ya llegó a la salida → victoria
        if jugador.posicion() == mapa.salida:
            tiempo_final = time.monotonic()
            duracion = tiempo_final - tiempo_inicio
            puntaje = calcular_puntaje_escapa(
                duracion_segundos=duracion,
                num_enemigos=len(enemigos),
                factor_dificultad=1.0,  # luego puedes usar niveles de dificultad
            )
            print("\n🎉 ¡Has llegado a la salida! (Modo Escapa)")
            print(f"Tiempo: {duracion:.1f} s")
            print(f"Puntaje: {puntaje}")
            input("\nEnter para volver al menú...")
            return

        # 2) Comprobar si algún enemigo está sobre el jugador → derrota
        for enemigo in enemigos:
            if enemigo.vivo and enemigo.posicion == jugador.posicion():
                print("\n💀 ¡Un cazador te atrapó! Game Over.")
                input("\nEnter para volver al menú...")
                return

        comando = leer_entrada_usuario()

        if comando == "q":
            print("Saliendo al menú principal...")
            return

        if comando == "r":
            # Toggle de correr
            if jugador.corriendo:
                jugador.detener_correr()
            else:
                if not jugador.iniciar_correr():
                    print("No tienes suficiente energía para correr.")
                    input("Enter para continuar...")
            continue

        # Direcciones
        dx, dy = 0, 0
        if comando == "w":
            dy = -1
        elif comando == "s":
            dy = 1
        elif comando == "a":
            dx = -1
        elif comando == "d":
            dx = 1
        else:
            # Comando inválido o vacío, simplemente continúa
            continue

        # 3) Mover jugador (puede moverse 1 o 2 casillas si corre)
        se_movio = jugador.mover(dx, dy, mapa)
        if not se_movio:
            print("No puedes moverte a esa casilla (muro o fuera del mapa).")
            input("Enter para continuar...")
            continue

        # 4) Luego de mover al jugador, comprobar si se lanzó contra un enemigo
        for enemigo in enemigos:
            if enemigo.vivo and enemigo.posicion == jugador.posicion():
                print("\n💀 ¡Has chocado contra un cazador! Game Over.")
                input("\nEnter para volver al menú...")
                return

        # 5) Mover enemigos (1 casilla) persiguiendo al jugador
        for enemigo in enemigos:
            enemigo.actualizar(mapa, jugador.posicion(), MODO_ESCAPA)

        # 6) Comprobar otra vez colisiones tras mover enemigos
        for enemigo in enemigos:
            if enemigo.vivo and enemigo.posicion == jugador.posicion():
                print("\n💀 ¡Un cazador te alcanzó! Game Over.")
                input("\nEnter para volver al menú...")
                return


# ======================================================
#                 MODO CAZADOR
# ======================================================

def jugar_modo_cazador() -> None:
    ancho = 20
    alto = 12

    mapa = generar_mapa(ancho, alto)
    inicio_x, inicio_y = mapa.inicio_jugador

    jugador = Jugador(x=inicio_x, y=inicio_y)

    # En este modo, el jugador persigue a los enemigos
    enemigos = crear_enemigos_iniciales(mapa, NUM_ENEMIGOS_INICIALES)

    enemigos_atrapados = 0
    enemigos_escapados = 0

    while True:
        limpiar_pantalla()

        print("=== MODO CAZADOR ===")
        print(f"Inicio del jugador: {mapa.inicio_jugador}")
        print(f"Salida: {mapa.salida}")
        print(f"Enemigos vivos: {len([e for e in enemigos if e.vivo])}")
        print(f"Enemigos atrapados: {enemigos_atrapados}")
        print(f"Enemigos escapados: {enemigos_escapados}")
        puntaje = calcular_puntaje_cazador(enemigos_atrapados, enemigos_escapados)
        print(f"Puntaje actual: {puntaje}")
        print()

        posiciones_enemigos = [e.posicion for e in enemigos if e.vivo]

        mapa.mostrar_en_consola(
            pos_jugador=jugador.posicion(),
            posiciones_enemigos=posiciones_enemigos,
        )

        print()
        print("Energía:", jugador.obtener_barra_energia())
        print("(R para activar/desactivar correr)")
        print("Ahora TÚ eres el cazador: si pisas una 'E', lo atrapas.")
        print("Si un enemigo llega a la salida, pierdes puntos.")
        print()

        comando = leer_entrada_usuario()

        if comando == "q":
            print("Saliendo al menú principal...")
            return

        if comando == "r":
            if jugador.corriendo:
                jugador.detener_correr()
            else:
                if not jugador.iniciar_correr():
                    print("No tienes suficiente energía para correr.")
                    input("Enter para continuar...")
            continue

        dx, dy = 0, 0
        if comando == "w":
            dy = -1
        elif comando == "s":
            dy = 1
        elif comando == "a":
            dx = -1
        elif comando == "d":
            dx = 1
        else:
            continue

        # Mover jugador
        se_movio = jugador.mover(dx, dy, mapa)
        if not se_movio:
            print("No puedes moverte a esa casilla.")
            input("Enter para continuar...")
            continue

        # Comprobar si atrapó a algún enemigo
        for enemigo in enemigos:
            if enemigo.vivo and enemigo.posicion == jugador.posicion():
                enemigo.vivo = False
                enemigos_atrapados += 1
                # Respawn simple en otra posición válida
                # (puedes mover esto a una función aparte si quieres)
                ancho = mapa.ancho
                alto = mapa.alto
                while True:
                    ex = random.randint(0, ancho - 1)
                    ey = random.randint(0, alto - 1)
                    if (ex, ey) != mapa.salida and mapa.es_transitable_por_enemigo(ex, ey):
                        enemigo.respawnear((ex, ey))
                        break

        # Mover enemigos para que HUYAN del jugador
        for enemigo in enemigos:
            enemigo.actualizar(mapa, jugador.posicion(), MODO_CAZADOR)

        # Comprobar si alguno llegó a la salida (enemigo escapado)
        for enemigo in enemigos:
            if enemigo.vivo and enemigo.posicion == mapa.salida:
                enemigos_escapados += 1
                # Reaparecerlo en otra posición
                ancho = mapa.ancho
                alto = mapa.alto
                while True:
                    ex = random.randint(0, ancho - 1)
                    ey = random.randint(0, alto - 1)
                    if (ex, ey) != mapa.salida and mapa.es_transitable_por_enemigo(ex, ey):
                        enemigo.respawnear((ex, ey))
                        break

        # Criterio de fin simple: si el puntaje baja de -200, termina
        puntaje = calcular_puntaje_cazador(enemigos_atrapados, enemigos_escapados)
        if puntaje <= -200:
            print("\n💀 Has perdido demasiados enemigos. Fin de la partida.")
            print(f"Puntaje final: {puntaje}")
            input("\nEnter para volver al menú...")
            return


# ======================================================
#                 MENÚ PRINCIPAL
# ======================================================

def main():
    while True:
        limpiar_pantalla()
        print("=== LABERINTO – PROYECTO II ===")
        print("1) Jugar Modo Escapa")
        print("2) Jugar Modo Cazador")
        print("Q) Salir")
        opcion = input("Elige una opción: ").strip().lower()

        if opcion == "1":
            jugar_modo_escapa()
        elif opcion == "2":
            jugar_modo_cazador()
        elif opcion == "q":
            print("¡Hasta luego!")
            sys.exit(0)
        else:
            print("Opción no válida.")
            input("Enter para continuar...")


if __name__ == "__main__":
    main()

