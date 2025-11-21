from typing import List, Tuple
import random

import pygame

from src.mapa import generar_mapa
from src.mapa.mapa import Mapa
from src.puntuacion import calcular_puntaje_escapa
from src.mapa.casillas import COD_CAMINO, COD_MURO, COD_TUNEL, COD_LIANA
from src.entidades import Enemigo, Jugador, MODO_ESCAPA, MODO_CAZADOR, Trampa


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
COLOR_TRAMPA = (255, 0, 255)  # morado para trampas


# ----- Configuración de trampas -----
MAX_TRAMPAS_ACTIVAS = 3
COOLDOWN_TRAMPA = 5.0             # segundos entre colocaciones
RESPAWN_ENEMIGO_TRAMPA = 10.0     # segundos para respawn de enemigos muertos por trampa


def _dibujar_mapa(
    pantalla: pygame.Surface,
    mapa: Mapa,
    pos_jugador: Tuple[int, int],
    posiciones_enemigos: List[Tuple[int, int]],
    posiciones_trampas: List[Tuple[int, int]],
) -> None:
    pantalla.fill(COLOR_FONDO)

    enemigos_set = set(posiciones_enemigos)
    trampas_set = set(posiciones_trampas)

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

    # Dibujar trampas
    for tx, ty in trampas_set:
        rect_trampa = pygame.Rect(tx * TAM_CELDA, ty * TAM_CELDA, TAM_CELDA, TAM_CELDA)
        pygame.draw.rect(pantalla, COLOR_TRAMPA, rect_trampa)

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
    pygame.display.set_caption(f"Laberinto - Modo {modo.upper()}")

    reloj = pygame.time.Clock()

    tiempo_inicio = pygame.time.get_ticks() / 1000.0

    # Crear jugador y enemigos
    jx, jy = mapa.inicio_jugador
    jugador = Jugador(x=jx, y=jy)

    enemigos: List[Enemigo] = []
    sx, sy = mapa.salida
    for _ in range(3):
        enemigos.append(Enemigo(sx, sy))

    # Trampas
    trampas: List[Trampa] = []
    ultima_trampa = 0.0  # tiempo en segundos
    enemigos_matados_trampa = 0

    ejecutando = True
    frame = 0

    while ejecutando:
        # Tiempo actual en segundos
        frame += 1
        tiempo_actual = pygame.time.get_ticks() / 1000.0

        # ----- Manejo de eventos -----
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    ejecutando = False
                else:
                    # Movimiento del jugador
                    _manejar_tecla_movimiento(evento.key, mapa, jugador)

                    # Colocar trampa solo en MODO_ESCAPA
                    if modo == MODO_ESCAPA and evento.key == pygame.K_t:
                        if _intentar_colocar_trampa(
                            jugador,
                            mapa,
                            trampas,
                            tiempo_actual,
                            ultima_trampa,
                        ):
                            ultima_trampa = tiempo_actual

        # ----- Actualizar enemigos -----
               # ----- Actualizar enemigos (más lentos) -----
        # Solo se mueven cada 3 frames (puedes ajustar)
        MOVER_CADA = 3

        if frame % MOVER_CADA == 0:
            for enemigo in enemigos:
                enemigo.actualizar(mapa, jugador.posicion(), modo)


        # ----- Trampas: matar enemigos que las pisen -----
        trampas_restantes: List[Trampa] = []
        for trampa in trampas:
            trampa_ocupo_enemigo = False
            for enemigo in enemigos:
                if enemigo.vivo and enemigo.posicion == trampa.posicion():
                    enemigo.matar(tiempo_actual)
                    enemigos_matados_trampa += 1
                    trampa_ocupo_enemigo = True
            if not trampa_ocupo_enemigo:
                trampas_restantes.append(trampa)
        trampas = trampas_restantes

        # ----- Respawn de enemigos muertos por trampas -----
        for enemigo in enemigos:
            if enemigo.listo_para_respawn(tiempo_actual, RESPAWN_ENEMIGO_TRAMPA):
                ex, ey = _buscar_posicion_valida_enemigo(mapa)
                enemigo.respawnear((ex, ey))

        # ----- Comprobar condiciones sencillas de fin -----
        if modo == MODO_ESCAPA and jugador.posicion() == mapa.salida:
                 tiempo_fin = tiempo_actual
                 duracion = tiempo_fin - tiempo_inicio

                 puntaje = calcular_puntaje_escapa(
                    duracion_segundos=duracion,
                    num_enemigos=len(enemigos),
                    factor_dificultad=1.0,        # luego lo ligamos a niveles
                    enemigos_eliminados_trampa=enemigos_matados_trampa,
                    )    

                 print("¡Has escapado del laberinto!")
                 print(f"Tiempo: {duracion:.1f} s")
                 print(f"Enemigos muertos por trampa: {enemigos_matados_trampa}")
                 print(f"Puntaje total (modo Escapa): {puntaje}")
                 ejecutando = False


        if any(enemigo.posicion == jugador.posicion() for enemigo in enemigos):
            if modo == MODO_ESCAPA:
                print("Te ha atrapado un cazador. Game Over.")
            else:
                print("Te encontraste con un enemigo (aquí puedes definir la regla).")
            ejecutando = False

        # ----- Dibujar -----
        posiciones_enemigos = [e.posicion for e in enemigos]
        # OJO: aquí usamos t.posicion() para obtener (x, y)
        posiciones_trampas = [t.posicion() for t in trampas]

        _dibujar_mapa(
            pantalla,
            mapa,
            jugador.posicion(),
            posiciones_enemigos,
            posiciones_trampas,
        )
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
        jugador.mover(dx, dy, mapa)


def _buscar_posicion_valida_enemigo(mapa: Mapa) -> Tuple[int, int]:
    """
    Devuelve una posición válida para respawn de enemigos:
    - No es muro
    - Es transitable para enemigo
    - No es inicio del jugador ni salida
    """
    while True:
        ex = random.randint(0, mapa.ancho - 1)
        ey = random.randint(0, mapa.alto - 1)

        if (ex, ey) == mapa.inicio_jugador or (ex, ey) == mapa.salida:
            continue

        if not mapa.es_transitable_por_enemigo(ex, ey):
            continue

        return ex, ey


def _intentar_colocar_trampa(
    jugador: Jugador,
    mapa: Mapa,
    trampas: List[Trampa],
    tiempo_actual: float,
    ultima_trampa: float,
) -> bool:
    """
    Intenta colocar una trampa en la posición actual del jugador
    respetando:
      - Máximo de trampas activas
      - Cooldown entre colocaciones
    Devuelve True si se colocó, False si no.
    """
    if len(trampas) >= MAX_TRAMPAS_ACTIVAS:
        print("Ya tienes el máximo de trampas activas.")
        return False

    if tiempo_actual - ultima_trampa < COOLDOWN_TRAMPA:
        restante = COOLDOWN_TRAMPA - (tiempo_actual - ultima_trampa)
        print(f"Aún no puedes colocar otra trampa. Espera {restante:.1f} s.")
        return False

    tx, ty = jugador.posicion()

    # No poner trampa donde no puede estar el jugador (por seguridad)
    if not mapa.es_transitable_por_jugador(tx, ty):
        print("No puedes colocar una trampa aquí.")
        return False

    # Evitar duplicar trampa en la misma casilla
    if any(t.posicion() == (tx, ty) for t in trampas):
        print("Ya hay una trampa en esta casilla.")
        return False

    trampa = Trampa(tx, ty, tiempo_colocacion=tiempo_actual)
    trampas.append(trampa)
    print("Trampa colocada.")
    return True
