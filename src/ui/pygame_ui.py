from typing import List, Tuple, Optional
import random

import pygame

from src.mapa import generar_mapa
from src.mapa.mapa import Mapa
from src.mapa.casillas import COD_CAMINO, COD_MURO, COD_TUNEL, COD_LIANA
from src.entidades import Enemigo, Jugador, MODO_ESCAPA, MODO_CAZADOR, Trampa
from src.puntuacion import (
    calcular_puntaje_escapa,
    calcular_puntaje_cazador,
    registrar_puntaje,
)

# ------------------ Configuración visual ------------------

TAM_CELDA = 32          # tamaño de cada casilla
FPS = 10                # frames por segundo
ALTURA_HUD = 80         # banda superior para HUD

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
COLOR_TEXTO = (255, 255, 255)

# Trampas
MAX_TRAMPAS_ACTIVAS = 3
COOLDOWN_TRAMPA = 5.0           # segundos entre trampas
RESPAWN_ENEMIGO_TRAMPA = 10.0   # respawn de enemigos muertos por trampa


# ----------------------------------------------------------
# Dibujo del mapa (en la parte de abajo, debajo del HUD)
# ----------------------------------------------------------
def _dibujar_mapa(
    pantalla: pygame.Surface,
    mapa: Mapa,
    offset_y: int,
    pos_jugador: Tuple[int, int],
    posiciones_enemigos: List[Tuple[int, int]],
    posiciones_trampas: List[Tuple[int, int]],
) -> None:
    enemigos_set = set(posiciones_enemigos)
    trampas_set = set(posiciones_trampas)

    for y in range(mapa.alto):
        for x in range(mapa.ancho):
            casilla = mapa.obtener_casilla(x, y)
            rect = pygame.Rect(
                x * TAM_CELDA,
                offset_y + y * TAM_CELDA,
                TAM_CELDA,
                TAM_CELDA,
            )

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

    # Salida
    sx, sy = mapa.salida
    rect_salida = pygame.Rect(
        sx * TAM_CELDA,
        offset_y + sy * TAM_CELDA,
        TAM_CELDA,
        TAM_CELDA,
    )
    pygame.draw.rect(pantalla, COLOR_SALIDA, rect_salida)

    # Trampas
    for tx, ty in trampas_set:
        rect_trampa = pygame.Rect(
            tx * TAM_CELDA,
            offset_y + ty * TAM_CELDA,
            TAM_CELDA,
            TAM_CELDA,
        )
        pygame.draw.rect(pantalla, COLOR_TRAMPA, rect_trampa)

    # Jugador
    jx, jy = pos_jugador
    rect_jugador = pygame.Rect(
        jx * TAM_CELDA,
        offset_y + jy * TAM_CELDA,
        TAM_CELDA,
        TAM_CELDA,
    )
    pygame.draw.rect(pantalla, COLOR_JUGADOR, rect_jugador)

    # Enemigos
    for ex, ey in enemigos_set:
        rect_enemigo = pygame.Rect(
            ex * TAM_CELDA,
            offset_y + ey * TAM_CELDA,
            TAM_CELDA,
            TAM_CELDA,
        )
        pygame.draw.rect(pantalla, COLOR_ENEMIGO, rect_enemigo)


# ----------------------------------------------------------
# Lógica principal del juego (con HUD, correr y puntajes)
# ----------------------------------------------------------
def ejecutar_juego(
    modo: str = MODO_ESCAPA,
    nombre_jugador: Optional[str] = None,
) -> None:
    pygame.init()

    # Generar mapa
    ancho, alto = 20, 15
    mapa: Mapa = generar_mapa(ancho, alto)

    # Ventana: alto del mapa + banda HUD arriba
    ancho_px = mapa.ancho * TAM_CELDA
    alto_px = ALTURA_HUD + mapa.alto * TAM_CELDA
    pantalla = pygame.display.set_mode((ancho_px, alto_px))
    pygame.display.set_caption(f"Laberinto - Modo {modo.upper()}")

    reloj = pygame.time.Clock()
    fuente_hud = pygame.font.SysFont(None, 24)

    # Tiempo de inicio
    tiempo_inicio = pygame.time.get_ticks() / 1000.0

    # Jugador y enemigos
    jx, jy = mapa.inicio_jugador
    jugador = Jugador(x=jx, y=jy)

    enemigos: List[Enemigo] = []
    sx, sy = mapa.salida
    for _ in range(3):
        enemigos.append(Enemigo(sx, sy))

    # Trampas (modo Escapa)
    trampas: List[Trampa] = []
    ultima_trampa = 0.0
    enemigos_matados_trampa = 0

    # Contadores modo Cazador
    enemigos_atrapados = 0
    enemigos_escapados = 0

    ejecutando = True
    frame = 0

    while ejecutando:
        frame += 1
        tiempo_actual = pygame.time.get_ticks() / 1000.0

        # ---------------- Eventos ----------------
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    ejecutando = False

                # R = correr ON/OFF
                elif evento.key == pygame.K_r:
                    if getattr(jugador, "corriendo", False):
                        jugador.detener_correr()
                    else:
                        if not jugador.iniciar_correr():
                            print("No tienes suficiente energía para correr.")

                else:
                    # Movimiento del jugador
                    _manejar_tecla_movimiento(evento.key, mapa, jugador)

                    # T = colocar trampa (solo Escapa)
                    if modo == MODO_ESCAPA and evento.key == pygame.K_t:
                        if _intentar_colocar_trampa(
                            jugador,
                            mapa,
                            trampas,
                            tiempo_actual,
                            ultima_trampa,
                        ):
                            ultima_trampa = tiempo_actual

        # ---------------- Enemigos ----------------
        MOVER_CADA = 3  # enemigos más lentos que el jugador
        if frame % MOVER_CADA == 0:
            for enemigo in enemigos:
                enemigo.actualizar(mapa, jugador.posicion(), modo)

        # Trampas matan enemigos (Escapa)
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

        # Respawn de enemigos muertos
        for enemigo in enemigos:
            if enemigo.listo_para_respawn(tiempo_actual, RESPAWN_ENEMIGO_TRAMPA):
                ex, ey = _buscar_posicion_valida_enemigo(mapa)
                enemigo.respawnear((ex, ey))

        # ---------------- Reglas de fin ----------------
        if modo == MODO_ESCAPA:
            # Victoria
            if jugador.posicion() == mapa.salida:
                tiempo_fin = tiempo_actual
                duracion = tiempo_fin - tiempo_inicio

                puntaje = calcular_puntaje_escapa(
                    duracion_segundos=duracion,
                    num_enemigos=len(enemigos),
                    factor_dificultad=1.0,
                    enemigos_eliminados_trampa=enemigos_matados_trampa,
                )

                print("🎉 ¡Has escapado del laberinto! (Modo Escapa)")
                if nombre_jugador:
                    print(f"Jugador: {nombre_jugador}")
                print(f"Tiempo: {duracion:.1f} s")
                print(f"Enemigos muertos por trampa: {enemigos_matados_trampa}")
                print(f"Puntaje total (modo Escapa): {puntaje}")

                if nombre_jugador:
                    registrar_puntaje(MODO_ESCAPA, nombre_jugador, puntaje)

                ejecutando = False

            # Derrota
            elif any(enemigo.posicion == jugador.posicion() for enemigo in enemigos):
                print("💀 Te ha atrapado un cazador. Game Over (Modo Escapa).")
                if nombre_jugador:
                    print(f"Jugador: {nombre_jugador}")
                ejecutando = False

        elif modo == MODO_CAZADOR:
            # Jugador atrapa enemigos
            for enemigo in enemigos:
                if enemigo.vivo and enemigo.posicion == jugador.posicion():
                    enemigos_atrapados += 1
                    ex, ey = _buscar_posicion_valida_enemigo(mapa)
                    enemigo.respawnear((ex, ey))

            # Enemigos que llegan a la salida -> escaparon
            for enemigo in enemigos:
                if enemigo.vivo and enemigo.posicion == mapa.salida:
                    enemigos_escapados += 1
                    ex, ey = _buscar_posicion_valida_enemigo(mapa)
                    enemigo.respawnear((ex, ey))

            puntaje = calcular_puntaje_cazador(
                enemigos_atrapados, enemigos_escapados
            )

            if puntaje <= -200:
                print("💀 Has perdido demasiados enemigos. Fin de la partida (Modo Cazador).")
                if nombre_jugador:
                    print(f"Jugador: {nombre_jugador}")
                    registrar_puntaje(MODO_CAZADOR, nombre_jugador, puntaje)
                print(f"Enemigos atrapados: {enemigos_atrapados}")
                print(f"Enemigos escapados: {enemigos_escapados}")
                print(f"Puntaje final (modo Cazador): {puntaje}")
                ejecutando = False

        # ---------------- Dibujo (mapa + HUD) ----------------
        pantalla.fill(COLOR_FONDO)

        posiciones_enemigos = [e.posicion for e in enemigos]
        posiciones_trampas = [t.posicion() for t in trampas]

        _dibujar_mapa(
            pantalla,
            mapa,
            ALTURA_HUD,
            jugador.posicion(),
            posiciones_enemigos,
            posiciones_trampas,
        )

        # HUD en la banda superior
        hud_y = 5

        if nombre_jugador:
            texto = fuente_hud.render(f"Jugador: {nombre_jugador}", True, COLOR_TEXTO)
            pantalla.blit(texto, (10, hud_y))
            hud_y += 20

        # Energía del jugador
        try:
            barra_energia = jugador.obtener_barra_energia()
        except AttributeError:
            barra_energia = "N/A"
        texto = fuente_hud.render(f"Energía: {barra_energia}", True, COLOR_TEXTO)
        pantalla.blit(texto, (10, hud_y))
        hud_y += 20

        # Estado de correr
        estado_corriendo = "ON" if getattr(jugador, "corriendo", False) else "OFF"
        texto = fuente_hud.render("Correr (R): " + estado_corriendo, True, COLOR_TEXTO)
        pantalla.blit(texto, (10, hud_y))
        hud_y += 20

        # Info por modo
        if modo == MODO_ESCAPA:
            texto = fuente_hud.render(
                f"Modo ESCAPA | Trampas: {len(trampas)}/{MAX_TRAMPAS_ACTIVAS}",
                True,
                COLOR_TEXTO,
            )
            pantalla.blit(texto, (10, hud_y))
        elif modo == MODO_CAZADOR:
            puntaje_actual = calcular_puntaje_cazador(
                enemigos_atrapados, enemigos_escapados
            )
            texto = fuente_hud.render(
                f"Modo CAZADOR | Atr: {enemigos_atrapados}  "
                f"Esc: {enemigos_escapados}  Pts: {puntaje_actual}",
                True,
                COLOR_TEXTO,
            )
            pantalla.blit(texto, (10, hud_y))

        pygame.display.flip()
        reloj.tick(FPS)

    pygame.quit()


# ----------------------------------------------------------
# Funciones auxiliares
# ----------------------------------------------------------
def _manejar_tecla_movimiento(tecla: int, mapa: Mapa, jugador: Jugador) -> None:
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
    if len(trampas) >= MAX_TRAMPAS_ACTIVAS:
        print("Ya tienes el máximo de trampas activas.")
        return False

    if tiempo_actual - ultima_trampa < COOLDOWN_TRAMPA:
        restante = COOLDOWN_TRAMPA - (tiempo_actual - ultima_trampa)
        print(f"Aún no puedes colocar otra trampa. Espera {restante:.1f} s.")
        return False

    tx, ty = jugador.posicion()

    if not mapa.es_transitable_por_jugador(tx, ty):
        print("No puedes colocar una trampa aquí.")
        return False

    if any(t.posicion() == (tx, ty) for t in trampas):
        print("Ya hay una trampa en esta casilla.")
        return False

    trampa = Trampa(tx, ty, tiempo_colocacion=tiempo_actual)
    trampas.append(trampa)
    print("Trampa colocada.")
    return True
