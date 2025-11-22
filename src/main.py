# src/main.py
import sys

from src.ui import ejecutar_juego, pedir_nombre, mostrar_menu
from src.entidades import MODO_ESCAPA, MODO_CAZADOR


def main() -> None:
    # Primero: pedir nombre en una ventana gráfica
    nombre = pedir_nombre()

    while True:
        # Menú gráfico: devuelve qué hacer y cuántos enemigos
        accion, num_enemigos = mostrar_menu(nombre)

        if accion == "salir" or num_enemigos is None:
            print("¡Hasta luego!")
            sys.exit(0)

        if accion == "escapa":
            ejecutar_juego(MODO_ESCAPA, nombre, num_enemigos)
        elif accion == "cazador":
            ejecutar_juego(MODO_CAZADOR, nombre, num_enemigos)
        # tras terminar una partida, el bucle vuelve a mostrar el menú gráfico


if __name__ == "__main__":
    main()

