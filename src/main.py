from src.mapa import generar_mapa


def main():
    ancho = 20
    alto = 12

    mapa = generar_mapa(ancho, alto)

    print("Inicio del jugador:", mapa.inicio_jugador)
    print("Salida:", mapa.salida)
    print()
    mapa.mostrar_en_consola(pos_jugador=mapa.inicio_jugador)


if __name__ == "__main__":
    main()
