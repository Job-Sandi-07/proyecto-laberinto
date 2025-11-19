import os
import sys
import random
from typing import List

from src.mapa import generar_mapa
from src.jugador import Jugador
from src.entidades import Enemigo, MODO_ESCAPA


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


def main():
    ancho = 20
    alto = 12

    mapa = generar_mapa(ancho, alto)
    inicio_x, inicio_y = mapa.inicio_jugador

    jugador = Jugador(x=inicio_x, y=inicio_y)

    # Crear enemigos iniciales para modo Escapa
    enemigos = crear_enemigos_iniciales(mapa, NUM_ENEMIGOS_INICIALES)

    while True:
        limpiar_pantalla()

        print("=== Demo Fase 2+3: Jugador + Energía + Enemigos (Modo Escapa) ===")
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

        # 1) Comprobar si ya llegó a la salida
        if jugador.posicion() == mapa.salida:
            print("\n🎉 ¡Has llegado a la salida! (Modo Escapa, con enemigos básicos)")
            break

        # 2) Comprobar si algún enemigo está sobre el jugador (por seguridad)
        for enemigo in enemigos:
            if enemigo.vivo and enemigo.posicion == jugador.posicion():
                print("\n💀 ¡Un cazador te atrapó! Game Over.")
                sys.exit(0)

        comando = leer_entrada_usuario()

        if comando == "q":
            print("Saliendo del juego...")
            sys.exit(0)

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
                sys.exit(0)

        # 5) Mover enemigos (1 casilla) persiguiendo al jugador
        for enemigo in enemigos:
            enemigo.actualizar(mapa, jugador.posicion(), MODO_ESCAPA)

        # 6) Comprobar otra vez colisiones tras mover enemigos
        for enemigo in enemigos:
            if enemigo.vivo and enemigo.posicion == jugador.posicion():
                print("\n💀 ¡Un cazador te alcanzó! Game Over.")
                sys.exit(0)


if __name__ == "__main__":
    main()

