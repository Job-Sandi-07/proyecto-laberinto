import random
from typing import Tuple, List

from .casillas import COD_CAMINO, COD_MURO
from .mapa import Mapa


def generar_matriz_basica(ancho: int, alto: int) -> Tuple[List[List[int]], Tuple[int, int], Tuple[int, int]]:
    """
    Genera una matriz aleatoria con al menos un camino desde el inicio hasta la salida.
    Por ahora solo usamos CAMINO y MURO.
    """

    # Empezamos con todo lleno de muros
    matriz = [[COD_MURO for _ in range(ancho)] for _ in range(alto)]

    # Definimos inicio y salida dentro del mapa (no en los bordes)
    inicio = (1, 1)
    salida = (ancho - 2, alto - 2)

    x, y = inicio
    matriz[y][x] = COD_CAMINO

    # Caminata aleatoria "dirigida" hasta la salida (garantiza un camino)
    while (x, y) != salida:
        opciones = []
        if x < salida[0]:
            opciones.append((1, 0))
        if y < salida[1]:
            opciones.append((0, 1))
        # agregamos algo de aleatoriedad
        opciones.extend([(0, -1), (-1, 0)])

        dx, dy = random.choice(opciones)
        nx, ny = x + dx, y + dy

        # Nos mantenemos dentro de los límites internos
        if 1 <= nx < ancho - 1 and 1 <= ny < alto - 1:
            x, y = nx, ny
            matriz[ny][nx] = COD_CAMINO

    # Abrimos algunos caminos extra al azar para que no sea un pasillo feo
    cantidad_extra = int(ancho * alto * 0.2)
    for _ in range(cantidad_extra):
        rx = random.randint(1, ancho - 2)
        ry = random.randint(1, alto - 2)
        matriz[ry][rx] = COD_CAMINO

    return matriz, inicio, salida


def generar_mapa(ancho: int, alto: int) -> Mapa:
    """
    Genera un Mapa listo para usar.
    """
    matriz, inicio, salida = generar_matriz_basica(ancho, alto)
    return Mapa.desde_matriz(matriz, inicio, salida)
