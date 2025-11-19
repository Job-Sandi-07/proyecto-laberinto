from typing import List, Tuple

import pygame

from src.mapa import generar_mapa
from src.mapa.mapa import Mapa
from src.mapa.casillas import COD_CAMINO, COD_MURO, COD_TUNEL, COD_LIANA
from src.entidades import Enemigo, Jugador, MODO_ESCAPA, MODO_CAZADOR


# ----- Configuración visual -----
TAM_CELDA = 32  # tamaño de cada casilla en píxeles
FPS = 10        # frames por segundo


# Colores (R, G, B)
COLOR_FONDO = (0, 0, 0)
COLOR_CAMINO = (200, 200, 200)
COLOR_MURO = (50, 50, 50)
COLOR_TUNEL = (0, 0, 180)
COLOR_LIANA = (0, 150, 0)
COLOR_JUGADOR = (255, 255, 0)
COLOR_ENEMIGO = (200, 50, 50)
COLOR_SALIDA = (255, 140, 0)


def _dibujar_mapa(
    pantalla: pygame.Surface,
    mapa: Mapa,
    pos_jugador: Tuple[int, int],
    posiciones_enemigos: List[Tuple[int, int]],
) -> None:
    pantalla.fill(COLOR_FONDO)

    enemigos_set = set(posiciones_enemigos)

    for y in range(mapa.alto):
        for x in range(mapa.ancho):
            casilla = mapa.obtener_casilla(x, y)
            rect = pygame.Rect(x * TAM_CELDA, y * TAM_CELDA, TAM_CELDA, TAM_CELDA)

            # Elegir color según tipo de casilla
            if casilla.codigo == COD_CAMINO:
                color = COLOR_CAMINO
            elif casilla.codigo == COD_MURO:
                color = COLOR_MURO
            elif casilla.codigo == COD_TUNEL:
                color = COLOR_TUNEL
            elif casilla.codigo == COD_LIANA:
                color = COLOR_LIANA
            else:
                color = COLOR_CAMINO

            pygame.draw.rect(pantalla, color, rect)

    # Dibujar salida
    sx, sy = mapa.salida
    rect_salida = pygame.Rect(sx * TAM_CELDA, sy * TAM_CELDA, TAM_CELDA, TAM_CELDA)
    pygame.draw.rect(pantalla, COLOR_SALIDA, rect_salida)

    # Dibujar jugador
    jx, jy = pos_jugador
    rect_jugador = pygame.Rect(jx * TAM_CELDA, jy * TAM_CELDA, TAM_CELDA, TAM_CELDA)
    pygame.draw.rect(pantalla, COLOR_JUGADOR, rect_jugador)

    # Dibujar enemigos
    for ex, ey in enemigos_set:
        rect_enemigo = pygame.Rect(ex * TAM_CELDA, ey * TAM_CELDA, TAM_CELDA, TAM_CELDA)
        pygame.draw.rect(pantalla, COLOR_ENEMIGO, rect_enemigo)


def ejecutar_juego(modo: str = MODO_ESCAPA) -> None:
    """
    Inicia una partida con interfaz gráfica simple.

    modo:
        - MODO_ESCAPA: los enemigos persiguen al jugador.
        - MODO_CAZADOR: los enemigos huyen del jugador.
    """
    pygame.init()

    # Generar mapa
    ancho, alto = 20, 15
    mapa: Mapa = generar_mapa(ancho, alto)

    # Crear ventana
    pantalla = pygame.display.set_mode((mapa.ancho * TAM_CELDA, mapa.alto * TAM_CELDA))
    pygame.display.setCaption = pygame.display.set_caption(
        f"Laberinto - Modo {modo.upper()}"
    )

    reloj = pygame.time.Clock()

    # Crear jugador y enemigos
    jx, jy = mapa.inicio_jugador
    jugador = Jugador(x=jx, y=jy)

    enemigos: List[Enemigo] = []
    sx, sy = mapa.salida
    for _ in range(3):
        enemigos.append(Enemigo(sx, sy))

    ejecutando = True

    while ejecutando:
        # ----- Manejo de eventos -----
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    ejecutando = False
                else:
                    _manejar_tecla_movimiento(evento.key, mapa, jugador)

        # ----- Actualizar enemigos -----
        for enemigo in enemigos:
            enemigo.actualizar(mapa, jugador.posicion(), modo)

        # ----- Comprobar condiciones sencillas de fin -----
        if modo == MODO_ESCAPA and jugador.posicion() == mapa.salida:
            print("¡Has escapado del laberinto!")
            ejecutando = False

        if any(enemigo.posicion == jugador.posicion() for enemigo in enemigos):
            if modo == MODO_ESCAPA:
                print("Te ha atrapado un cazador. Game Over.")
            else:
                print("Te encontraste con un enemigo (aquí puedes definir la regla).")
            ejecutando = False

        # ----- Dibujar -----
        posiciones_enemigos = [e.posicion for e in enemigos]
        _dibujar_mapa(pantalla, mapa, jugador.posicion(), posiciones_enemigos)
        pygame.display.flip()

        reloj.tick(FPS)

    pygame.quit()  # volvemos al menú de main.py


def _manejar_tecla_movimiento(tecla: int, mapa: Mapa, jugador: Jugador) -> None:
    """
    Traduce teclas a movimiento del jugador.
    Por ahora: flechas o WASD, usando Jugador.mover(dx, dy, mapa).
    """
    dx, dy = 0, 0
    if tecla in (pygame.K_UP, pygame.K_w):
        dy = -1
    elif tecla in (pygame.K_DOWN, pygame.K_s):
        dy = 1
    elif tecla in (pygame.K_LEFT, pygame.K_a):
        dx = -1
    elif tecla in (pygame.K_RIGHT, pygame.K_d):
        dx = 1

    if dx != 0 or dy != 0:
        # Usamos tu método existente de Jugador
        jugador.mover(dx, dy, mapa)
