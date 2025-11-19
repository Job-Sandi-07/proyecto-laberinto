import sys

from src.ui import ejecutar_juego
from src.entidades import MODO_ESCAPA, MODO_CAZADOR


def main() -> None:
    while True:
        print("=== LABERINTO – PROYECTO II ===")
        print("1) Jugar Modo Escapa (interfaz gráfica)")
        print("2) Jugar Modo Cazador (interfaz gráfica)")
        print("Q) Salir")
        opcion = input("Elige una opción: ").strip().lower()

        if opcion == "1":
            ejecutar_juego(MODO_ESCAPA)
        elif opcion == "2":
            ejecutar_juego(MODO_CAZADOR)
        elif opcion == "q":
            print("¡Hasta luego!")
            sys.exit(0)
        else:
            print("Opción no válida.")
            input("Enter para continuar...")
            print()  # línea en blanco


if __name__ == "__main__":
    main()
