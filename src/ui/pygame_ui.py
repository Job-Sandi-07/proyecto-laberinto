from typing import List, Tuple, Optional
import random
import sys

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
from src.terrenos import (
    agregar_terrenos_especiales,
    aplicar_efecto_terreno_jugador,
    aplicar_efecto_terreno_enemigo,
    es_tunel,
    es_liana,
)
from src.musica.musica import iniciar_musica, detener_musica

TAM_CELDA = 32
FPS = 10
ALTURA_HUD = 120

COLOR_FONDO = (0, 0, 0)
COLOR_CAMINO = (200, 200, 200)
COLOR_MURO = (50, 50, 50)
COLOR_TUNEL = (0, 0, 180)
COLOR_LIANA = (0, 150, 0)
COLOR_JUGADOR = (255, 255, 0)
COLOR_ENEMIGO = (200, 50, 50)
COLOR_SALIDA = (255, 140, 0)
COLOR_TRAMPA = (255, 0, 255)
COLOR_TEXTO = (255, 255, 255)

MAX_TRAMPAS_ACTIVAS = 3
COOLDOWN_TRAMPA = 5.0
RESPAWN_ENEMIGO_TRAMPA = 10.0


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

            if es_tunel(x, y):
                color = COLOR_TUNEL
            elif es_liana(x, y):
                color = COLOR_LIANA
            else:
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

    sx, sy = mapa.salida
    rect_salida = pygame.Rect(
        sx * TAM_CELDA,
        offset_y + sy * TAM_CELDA,
        TAM_CELDA,
        TAM_CELDA,
    )
    pygame.draw.rect(pantalla, COLOR_SALIDA, rect_salida)

    for tx, ty in trampas_set:
        rect_trampa = pygame.Rect(
            tx * TAM_CELDA,
            offset_y + ty * TAM_CELDA,
            TAM_CELDA,
            TAM_CELDA,
        )
        pygame.draw.rect(pantalla, COLOR_TRAMPA, rect_trampa)

    jx, jy = pos_jugador
    rect_jugador = pygame.Rect(
        jx * TAM_CELDA,
        offset_y + jy * TAM_CELDA,
        TAM_CELDA,
        TAM_CELDA,
    )
    pygame.draw.rect(pantalla, COLOR_JUGADOR, rect_jugador)

    for ex, ey in enemigos_set:
        rect_enemigo = pygame.Rect(
            ex * TAM_CELDA,
            offset_y + ey * TAM_CELDA,
            TAM_CELDA,
            TAM_CELDA,
        )
        pygame.draw.rect(pantalla, COLOR_ENEMIGO, rect_enemigo)


def ejecutar_juego(
    modo: str = MODO_ESCAPA,
    nombre_jugador: Optional[str] = None,
    num_enemigos: int = 3,
) -> None:
    pygame.init()

    ancho, alto = 20, 15
    ancho_px = ancho * TAM_CELDA
    alto_px = ALTURA_HUD + alto * TAM_CELDA
    pantalla = pygame.display.set_mode((ancho_px, alto_px))
    pygame.display.set_caption(f"Laberinto - Modo {modo.upper()}")

    iniciar_musica(loop=True, volumen=0.4)

    reloj = pygame.time.Clock()
    fuente_hud = pygame.font.SysFont(None, 24)
    fuente_info = pygame.font.SysFont(None, 20)

    mapa: Mapa
    jugador: Jugador
    enemigos: List[Enemigo]
    trampas: List[Trampa]
    ultima_trampa: float
    enemigos_matados_trampa: int
    enemigos_atrapados: int
    enemigos_escapados: int
    vidas_restantes: int

    def crear_escenario() -> None:
        nonlocal mapa, jugador, enemigos, trampas
        nonlocal ultima_trampa, enemigos_matados_trampa
        nonlocal enemigos_atrapados, enemigos_escapados, vidas_restantes

        mapa = generar_mapa(ancho, alto)
        agregar_terrenos_especiales(mapa, prob_tunel=0.03, prob_liana=0.03)

        jx, jy = mapa.inicio_jugador
        jugador = Jugador(x=jx, y=jy)

        enemigos = []
        for _ in range(num_enemigos):
            ex, ey = _buscar_posicion_valida_enemigo(mapa)
            enemigos.append(Enemigo(ex, ey))

        trampas = []
        ultima_trampa = 0.0
        enemigos_matados_trampa = 0
        enemigos_atrapados = 0
        enemigos_escapados = 0

        if modo == MODO_ESCAPA:
            vidas_restantes = 3
        else:
            vidas_restantes = 0

    crear_escenario()

    tiempo_inicio = 0.0
    en_previa = True
    while en_previa:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                detener_musica()
                pygame.quit()
                sys.exit(0)
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
                elif evento.key == pygame.K_r:
                    crear_escenario()
                elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    tiempo_inicio = pygame.time.get_ticks() / 1000.0
                    en_previa = False

        pantalla.fill(COLOR_FONDO)

        posiciones_enemigos = [e.posicion for e in enemigos if e.vivo]
        posiciones_trampas = []

        _dibujar_mapa(
            pantalla,
            mapa,
            ALTURA_HUD,
            jugador.posicion(),
            posiciones_enemigos,
            posiciones_trampas,
        )

        hud_y = 5
        if nombre_jugador:
            t = fuente_hud.render(f"Jugador: {nombre_jugador}", True, COLOR_TEXTO)
            pantalla.blit(t, (10, hud_y))
            hud_y += 20

        t = fuente_hud.render("Energía: 100/100 (caminando)", True, COLOR_TEXTO)
        pantalla.blit(t, (10, hud_y))
        hud_y += 20

        t = fuente_hud.render("Correr (R): OFF", True, COLOR_TEXTO)
        pantalla.blit(t, (10, hud_y))
        hud_y += 20

        if modo == MODO_ESCAPA:
            t = fuente_hud.render(
                f"Modo ESCAPA | Cazadores: {num_enemigos}  Trampas: 0/{MAX_TRAMPAS_ACTIVAS}",
                True,
                COLOR_TEXTO,
            )
            pantalla.blit(t, (10, hud_y))
            hud_y += 20
            t = fuente_hud.render("Vidas: 3", True, COLOR_TEXTO)
            pantalla.blit(t, (10, hud_y))
        else:
            t = fuente_hud.render(
                f"Modo CAZADOR | Escapistas: {num_enemigos}",
                True,
                COLOR_TEXTO,
            )
            pantalla.blit(t, (10, hud_y))

        msg1 = "ENTER: empezar"
        msg2 = "R: nuevo laberinto  |  ESC: volver al menú"

        s1 = fuente_info.render(msg1, True, COLOR_TEXTO)
        s2 = fuente_info.render(msg2, True, COLOR_TEXTO)

        y_base = ALTURA_HUD - 35
        pantalla.blit(
            s1,
            (pantalla.get_width() // 2 - s1.get_width() // 2, y_base),
        )
        pantalla.blit(
            s2,
            (pantalla.get_width() // 2 - s2.get_width() // 2, y_base + 18),
        )

        pygame.display.flip()
        reloj.tick(FPS)

    ejecutando = True
    frame = 0

    while ejecutando:
        frame += 1
        tiempo_actual = pygame.time.get_ticks() / 1000.0

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                detener_musica()
                pygame.quit()
                sys.exit(0)
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    ejecutando = False
                elif evento.key == pygame.K_r:
                    if getattr(jugador, "corriendo", False):
                        jugador.detener_correr()
                    else:
                        if not jugador.iniciar_correr():
                            print("No tienes suficiente energía para correr.")
                else:
                    _manejar_tecla_movimiento(evento.key, mapa, jugador)
                    if modo == MODO_ESCAPA and evento.key == pygame.K_t:
                        if _intentar_colocar_trampa(
                            jugador,
                            mapa,
                            trampas,
                            tiempo_actual,
                            ultima_trampa,
                        ):
                            ultima_trampa = tiempo_actual

        MOVER_CADA = 3
        if frame % MOVER_CADA == 0:
            for enemigo in enemigos:
                if enemigo.vivo:
                    enemigo.actualizar(mapa, jugador.posicion(), modo)
                    aplicar_efecto_terreno_enemigo(mapa, enemigo)

        if modo == MODO_ESCAPA:
            trampas_restantes: List[Trampa] = []
            for trampa in trampas:
                ocupo = False
                for enemigo in enemigos:
                    if enemigo.vivo and enemigo.posicion == trampa.posicion():
                        enemigo.matar(tiempo_actual)
                        enemigos_matados_trampa += 1
                        ocupo = True
                if not ocupo:
                    trampas_restantes.append(trampa)
            trampas = trampas_restantes

            for enemigo in enemigos:
                if enemigo.listo_para_respawn(tiempo_actual, RESPAWN_ENEMIGO_TRAMPA):
                    ex, ey = _buscar_posicion_valida_enemigo(mapa)
                    enemigo.respawnear((ex, ey))

        if modo == MODO_ESCAPA:
            if jugador.posicion() == mapa.salida:
                tiempo_fin = tiempo_actual
                duracion = tiempo_fin - tiempo_inicio
                factor_dificultad = max(1.0, num_enemigos / 3.0)

                puntaje = calcular_puntaje_escapa(
                    duracion_segundos=duracion,
                    num_enemigos=num_enemigos,
                    factor_dificultad=factor_dificultad,
                    enemigos_eliminados_trampa=enemigos_matados_trampa,
                )

                if nombre_jugador:
                    registrar_puntaje(MODO_ESCAPA, nombre_jugador, puntaje)

                lineas = [
                    f"Jugador: {nombre_jugador}" if nombre_jugador else "",
                    f"Tiempo: {duracion:.1f} s",
                    f"Cazadores: {num_enemigos}",
                    f"Enemigos muertos por trampa: {enemigos_matados_trampa}",
                    f"Puntaje: {puntaje}",
                ]
                _mostrar_pantalla_fin(pantalla, "¡Victoria! (Modo Escapa)", lineas)
                ejecutando = False

            elif any(
                enemigo.vivo and enemigo.posicion == jugador.posicion()
                for enemigo in enemigos
            ):
                if vidas_restantes > 1:
                    vidas_restantes -= 1
                    print(f"Te han atrapado. Vidas restantes: {vidas_restantes}")
                    jx, jy = mapa.inicio_jugador
                    jugador.x, jugador.y = jx, jy
                else:
                    vidas_restantes -= 1
                    lineas = [
                        f"Jugador: {nombre_jugador}" if nombre_jugador else "",
                        "Te has quedado sin vidas.",
                        f"Cazadores: {num_enemigos}",
                    ]
                    _mostrar_pantalla_fin(pantalla, "Game Over (Modo Escapa)", lineas)
                    ejecutando = False

        elif modo == MODO_CAZADOR:
            for enemigo in enemigos:
                if enemigo.vivo and enemigo.posicion == jugador.posicion():
                    enemigos_atrapados += 1
                    enemigo.vivo = False

            for enemigo in enemigos:
                if enemigo.vivo and enemigo.posicion == mapa.salida:
                    enemigos_escapados += 1
                    enemigo.vivo = False

            if enemigos_atrapados == num_enemigos:
                puntaje = calcular_puntaje_cazador(
                    enemigos_atrapados, enemigos_escapados
                )
                if nombre_jugador:
                    registrar_puntaje(MODO_CAZADOR, nombre_jugador, puntaje)

                lineas = [
                    f"Jugador: {nombre_jugador}" if nombre_jugador else "",
                    f"Enemigos atrapados: {enemigos_atrapados}",
                    f"Enemigos escapados: {enemigos_escapados}",
                    f"Puntaje final: {puntaje}",
                ]
                _mostrar_pantalla_fin(pantalla, "¡Victoria! (Modo Cazador)", lineas)
                ejecutando = False
            else:
                vivos_restantes = any(e.vivo for e in enemigos)
                if not vivos_restantes and enemigos_atrapados < num_enemigos:
                    puntaje = calcular_puntaje_cazador(
                        enemigos_atrapados, enemigos_escapados
                    )
                    lineas = [
                        f"Jugador: {nombre_jugador}" if nombre_jugador else "",
                        "Algunos enemigos escaparon. No los cazaste a todos.",
                        f"Enemigos atrapados: {enemigos_atrapados}",
                        f"Enemigos escapados: {enemigos_escapados}",
                        f"Puntaje final: {puntaje}",
                    ]
                    _mostrar_pantalla_fin(
                        pantalla, "Game Over (Modo Cazador)", lineas
                    )
                    ejecutando = False

        pantalla.fill(COLOR_FONDO)

        posiciones_enemigos = [e.posicion for e in enemigos if e.vivo]
        posiciones_trampas = [t.posicion() for t in trampas]

        _dibujar_mapa(
            pantalla,
            mapa,
            ALTURA_HUD,
            jugador.posicion(),
            posiciones_enemigos,
            posiciones_trampas,
        )

        hud_y = 5
        if nombre_jugador:
            t = fuente_hud.render(f"Jugador: {nombre_jugador}", True, COLOR_TEXTO)
            pantalla.blit(t, (10, hud_y))
            hud_y += 20

        try:
            barra_energia = jugador.obtener_barra_energia()
        except AttributeError:
            barra_energia = "N/A"
        t = fuente_hud.render(f"Energía: {barra_energia}", True, COLOR_TEXTO)
        pantalla.blit(t, (10, hud_y))
        hud_y += 20

        estado_corriendo = "ON" if getattr(jugador, "corriendo", False) else "OFF"
        t = fuente_hud.render(f"Correr (R): {estado_corriendo}", True, COLOR_TEXTO)
        pantalla.blit(t, (10, hud_y))
        hud_y += 20

        if modo == MODO_ESCAPA:
            t = fuente_hud.render(
                f"Modo ESCAPA | Cazadores: {num_enemigos}  "
                f"Trampas: {len(trampas)}/{MAX_TRAMPAS_ACTIVAS}",
                True,
                COLOR_TEXTO,
            )
            pantalla.blit(t, (10, hud_y))
            hud_y += 20

            t = fuente_hud.render(f"Vidas: {vidas_restantes}", True, COLOR_TEXTO)
            pantalla.blit(t, (10, hud_y))
        else:
            puntaje_actual = calcular_puntaje_cazador(
                enemigos_atrapados, enemigos_escapados
            )
            t = fuente_hud.render(
                f"Modo CAZADOR | Escapistas: {num_enemigos}  "
                f"Atr: {enemigos_atrapados}  Esc: {enemigos_escapados}  "
                f"Pts: {puntaje_actual}",
                True,
                COLOR_TEXTO,
            )
            pantalla.blit(t, (10, hud_y))

        pygame.display.flip()
        reloj.tick(FPS)

    pygame.quit()


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
        aplicar_efecto_terreno_jugador(mapa, jugador)


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


def _mostrar_pantalla_fin(
    pantalla: pygame.Surface,
    titulo: str,
    lineas_info: List[str],
) -> None:
    fuente_titulo = pygame.font.SysFont(None, 48)
    fuente_texto = pygame.font.SysFont(None, 28)
    reloj = pygame.time.Clock()

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                detener_musica()
                pygame.quit()
                sys.exit(0)
            if evento.type == pygame.KEYDOWN:
                if evento.key in (
                    pygame.K_ESCAPE,
                    pygame.K_RETURN,
                    pygame.K_KP_ENTER,
                ):
                    return

        pantalla.fill(COLOR_FONDO)

        s_titulo = fuente_titulo.render(titulo, True, COLOR_TEXTO)
        pantalla.blit(
            s_titulo,
            (
                pantalla.get_width() // 2 - s_titulo.get_width() // 2,
                100,
            ),
        )

        y = 180
        for linea in lineas_info:
            if not linea:
                continue
            s = fuente_texto.render(linea, True, COLOR_TEXTO)
            pantalla.blit(
                s,
                (pantalla.get_width() // 2 - s.get_width() // 2, y),
            )
            y += 30

        ayuda = fuente_texto.render(
            "ENTER o ESC para volver al menú",
            True,
            COLOR_TEXTO,
        )
        pantalla.blit(
            ayuda,
            (
                pantalla.get_width() // 2 - ayuda.get_width() // 2,
                pantalla.get_height() - 60,
            ),
        )

        pygame.display.flip()
        reloj.tick(60)
