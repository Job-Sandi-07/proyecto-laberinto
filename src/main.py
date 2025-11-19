import os
import sys

from src.mapa import generar_mapa
from src.jugador import Jugador

def limpiar_pantalla() -> None:
    # No es perfecto, pero funciona en la mayoría de casos
    os.system("cls" if os.name == "nt" else "clear")


def leer_entrada_usuario() -> str:
    comando = input("Mover (WASD), R=correr, Q=salir: ").strip().lower()
    return comando[:1] if comando else ""



def main():
    ancho = 20
    alto = 12

    mapa = generar_mapa(ancho, alto)
    inicio_x, inicio_y = mapa.inicio_jugador

    jugador = Jugador(x=inicio_x, y=inicio_y)

    while True:
        limpiar_pantalla()

        print("=== Demo Fase 2: Jugador + Energía ===")
        print(f"Inicio del jugador: {mapa.inicio_jugador}")
        print(f"Salida: {mapa.salida}")
        print()

        # Mostrar mapa con el jugador
        mapa.mostrar_en_consola(pos_jugador=jugador.posicion())

        print()
        print("Energía:", jugador.obtener_barra_energia())
        print("(R para activar/desactivar correr)")

        # Comprobar si ya llegó a la salida
        if jugador.posicion() == mapa.salida:
            print("\n🎉 ¡Has llegado a la salida! (aún sin enemigos, pero el mapa funciona)")
            break

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
            # Comando inválido o vacío, simplemente continua
            continue

        se_movio = jugador.mover(dx, dy, mapa)
        if not se_movio:
            print("No puedes moverte a esa casilla (muro o fuera del mapa).")
            input("Enter para continuar...")

if __name__ == "__main__":
    main()
