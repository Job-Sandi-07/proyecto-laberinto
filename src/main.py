import sys

from src.ui import ejecutar_juego, pedir_nombre
from src.entidades import MODO_ESCAPA, MODO_CAZADOR
from src.puntuacion import obtener_top5


def mostrar_puntajes() -> None:
    print("=== TOP 5 - MODO ESCAPA ===")
    top_escapa = obtener_top5(MODO_ESCAPA)
    if not top_escapa:
        print("Sin registros aún.")
    else:
        for i, entrada in enumerate(top_escapa, start=1):
            print(f"{i}. {entrada['nombre']} - {entrada['puntaje']}")

    print("\n=== TOP 5 - MODO CAZADOR ===")
    top_cazador = obtener_top5(MODO_CAZADOR)
    if not top_cazador:
        print("Sin registros aún.")
    else:
        for i, entrada in enumerate(top_cazador, start=1):
            print(f"{i}. {entrada['nombre']} - {entrada['puntaje']}")

    input("\nEnter para volver al menú...")


def main() -> None:
    # Primero: pedir nombre en una ventana gráfica
    nombre = pedir_nombre()

    while True:
        print("=== LABERINTO – PROYECTO II ===")
        print(f"Jugador actual: {nombre}")
        print("1) Jugar Modo Escapa")
        print("2) Jugar Modo Cazador")
        print("3) Ver puntajes")
        print("Q) Salir")
        opcion = input("Elige una opción: ").strip().lower()

        if opcion == "1":
            ejecutar_juego(MODO_ESCAPA, nombre)
        elif opcion == "2":
            ejecutar_juego(MODO_CAZADOR, nombre)
        elif opcion == "3":
            mostrar_puntajes()
        elif opcion == "q":
            print("¡Hasta luego!")
            sys.exit(0)
        else:
            print("Opción no válida.")
            input("Enter para continuar...")
            print()


if __name__ == "__main__":
    main()
