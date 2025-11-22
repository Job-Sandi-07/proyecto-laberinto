# src/ui/menu_ui.py
from typing import Tuple, Optional

import pygame
import sys

from src.entidades import MODO_ESCAPA, MODO_CAZADOR
from src.puntuacion import obtener_top5
from src.musica.musica import iniciar_musica, detener_musica

ANCHO_VENTANA = 800
ALTO_VENTANA = 600

COLOR_FONDO = (0, 0, 0)
COLOR_TEXTO = (255, 255, 255)
COLOR_SELECCIONADO = (255, 255, 0)
COLOR_TITULO = (255, 255, 255)


def mostrar_menu(nombre_jugador: str) -> Tuple[str, Optional[int]]:
   
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
    pygame.display.set_caption("Menú principal - Laberinto")

    # Iniciar música de fondo (loop) si es posible
    iniciar_musica(loop=True, volumen=0.4)
    volumen = pygame.mixer.music.get_volume() if pygame.mixer.get_init() else 0.4

    fuente_titulo = pygame.font.SysFont(None, 36)
    fuente_opcion = pygame.font.SysFont(None, 28)
    reloj = pygame.time.Clock()

    opciones = [
        ("Jugar Modo Escapa", "escapa"),
        ("Jugar Modo Cazador", "cazador"),
        ("Ver puntajes", "puntajes"),
        ("Salir", "salir"),
    ]
    indice_seleccionado = 0

    ejecutando = True
    while ejecutando:
        for evento in pygame.event.get():
         if evento.type == pygame.QUIT:
                detener_musica()
                pygame.quit()
                sys.exit(0)

         if evento.type == pygame.KEYDOWN:
            
            if evento.key in (pygame.K_UP, pygame.K_w):
                indice_seleccionado = (indice_seleccionado - 1) % len(opciones)

            elif evento.key in (pygame.K_DOWN, pygame.K_s):
                indice_seleccionado = (indice_seleccionado + 1) % len(opciones)

            elif evento.key in (pygame.K_LEFT, pygame.K_a):
                volumen = max(0.0, volumen - 0.1)
                if pygame.mixer.get_init():
                    pygame.mixer.music.set_volume(volumen)

            elif evento.key in (pygame.K_RIGHT, pygame.K_d):
                volumen = min(1.0, volumen + 0.1)
                if pygame.mixer.get_init():
                    pygame.mixer.music.set_volume(volumen)

            # ENTER para activar la opción seleccionada
            elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                _, accion = opciones[indice_seleccionado]

                if accion == "escapa":
                    num = _pantalla_configurar_enemigos(
                        pantalla, fuente_titulo, fuente_opcion, "Modo Escapa"
                    )
                    if num is not None:
                        pygame.quit()
                        return "escapa", num

                elif accion == "cazador":
                    num = _pantalla_configurar_enemigos(
                        pantalla, fuente_titulo, fuente_opcion, "Modo Cazador"
                    )
                    if num is not None:
                        pygame.quit()
                        return "cazador", num

                elif accion == "puntajes":
                    _pantalla_puntajes(
                        pantalla, fuente_titulo, fuente_opcion, nombre_jugador
                    )

                elif accion == "salir":
                    detener_musica()
                    pygame.quit()
                    return "salir", None

        # Dibujar menú
        pantalla.fill(COLOR_FONDO)

        titulo = fuente_titulo.render("LABERINTO – PROYECTO II", True, COLOR_TITULO)
        pantalla.blit(
            titulo,
            (ANCHO_VENTANA // 2 - titulo.get_width() // 2, 60),
        )

        subtitulo = fuente_opcion.render(
            f"Jugador: {nombre_jugador}", True, COLOR_TEXTO
        )
        pantalla.blit(
            subtitulo,
            (ANCHO_VENTANA // 2 - subtitulo.get_width() // 2, 110),
        )

        inicio_y = 200
        separacion = 40
        for i, (texto, _) in enumerate(opciones):
            color = COLOR_SELECCIONADO if i == indice_seleccionado else COLOR_TEXTO
            superficie = fuente_opcion.render(texto, True, color)
            pantalla.blit(
                superficie,
                (ANCHO_VENTANA // 2 - superficie.get_width() // 2,
                 inicio_y + i * separacion),
            )

        ayuda = fuente_opcion.render(
            "W/S para moverse, ENTER para seleccionar",
            True,
            COLOR_TEXTO,
        )
        pantalla.blit(
            ayuda,
            (ANCHO_VENTANA // 2 - ayuda.get_width() // 2, ALTO_VENTANA - 60),
        )
        texto_vol = fuente_opcion.render(
            f"Volumen música: {int(volumen * 100)}%  (derecha o izquierda para ajustar)",
            True,
            COLOR_TEXTO,
        )
        
        pantalla.blit(
            texto_vol,
            (ANCHO_VENTANA // 2 - texto_vol.get_width() // 2, ALTO_VENTANA - 30),
        )

        pygame.display.flip()
        reloj.tick(60)

    detener_musica()
    pygame.quit()
    return "salir", None


def _pantalla_configurar_enemigos(
    pantalla: pygame.Surface,
    fuente_titulo: pygame.font.Font,
    fuente_texto: pygame.font.Font,
    titulo_modo: str,
) -> Optional[int]:
   
    reloj = pygame.time.Clock()
    num_enemigos = 3
    ejecutando = True

    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                detener_musica()
                pygame.quit()
                sys.exit(0)
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return None
                elif evento.key in (pygame.K_LEFT, pygame.K_a):
                    num_enemigos = max(1, num_enemigos - 1)
                elif evento.key in (pygame.K_RIGHT, pygame.K_d):
                    num_enemigos = min(10, num_enemigos + 1)
                elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    return num_enemigos

        pantalla.fill(COLOR_FONDO)

        titulo = fuente_titulo.render(
            f"{titulo_modo} - Dificultad", True, COLOR_TITULO
        )
        pantalla.blit(
            titulo,
            (ANCHO_VENTANA // 2 - titulo.get_width() // 2, 80),
        )

        texto = fuente_texto.render(
            f"Cantidad de enemigos: {num_enemigos}",
            True,
            COLOR_TEXTO,
        )
        pantalla.blit(
            texto,
            (ANCHO_VENTANA // 2 - texto.get_width() // 2, 180),
        )

        ayuda = fuente_texto.render(
            "A / D para cambiar, ENTER para aceptar, ESC para volver",
            True,
            COLOR_TEXTO,
        )
        pantalla.blit(
            ayuda,
            (ANCHO_VENTANA // 2 - ayuda.get_width() // 2, 240),
        )

        pygame.display.flip()
        reloj.tick(60)

    return None


def _pantalla_puntajes(
    pantalla: pygame.Surface,
    fuente_titulo: pygame.font.Font,
    fuente_texto: pygame.font.Font,
    nombre_jugador: str,
) -> None:
   
    reloj = pygame.time.Clock()

    top_escapa = obtener_top5(MODO_ESCAPA)
    top_cazador = obtener_top5(MODO_CAZADOR)

    ejecutando = True
    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                detener_musica()
                pygame.quit()
                sys.exit(0)
            if evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER):
                    return

        pantalla.fill(COLOR_FONDO)

        titulo = fuente_titulo.render("PUNTAJES", True, COLOR_TITULO)
        pantalla.blit(
            titulo,
            (ANCHO_VENTANA // 2 - titulo.get_width() // 2, 40),
        )

        subtitulo = fuente_texto.render(
            f"Jugador actual: {nombre_jugador}", True, COLOR_TEXTO
        )
        pantalla.blit(
            subtitulo,
            (ANCHO_VENTANA // 2 - subtitulo.get_width() // 2, 80),
        )

        # Columna izquierda: Escapa
        x_izq = 80
        y_inicio = 140
        titulo_escapa = fuente_texto.render("Top 5 - Modo Escapa", True, COLOR_TEXTO)
        pantalla.blit(titulo_escapa, (x_izq, y_inicio))
        y = y_inicio + 30
        if not top_escapa:
            texto = fuente_texto.render("Sin registros aún.", True, COLOR_TEXTO)
            pantalla.blit(texto, (x_izq, y))
        else:
            for i, entrada in enumerate(top_escapa, start=1):
                linea = f"{i}. {entrada['nombre']} - {entrada['puntaje']}"
                texto = fuente_texto.render(linea, True, COLOR_TEXTO)
                pantalla.blit(texto, (x_izq, y))
                y += 25

        # Columna derecha: Cazador
        x_der = ANCHO_VENTANA // 2 + 40
        y_inicio = 140
        titulo_cazador = fuente_texto.render("Top 5 - Modo Cazador", True, COLOR_TEXTO)
        pantalla.blit(titulo_cazador, (x_der, y_inicio))
        y = y_inicio + 30
        if not top_cazador:
            texto = fuente_texto.render("Sin registros aún.", True, COLOR_TEXTO)
            pantalla.blit(texto, (x_der, y))
        else:
            for i, entrada in enumerate(top_cazador, start=1):
                linea = f"{i}. {entrada['nombre']} - {entrada['puntaje']}"
                texto = fuente_texto.render(linea, True, COLOR_TEXTO)
                pantalla.blit(texto, (x_der, y))
                y += 25

        ayuda = fuente_texto.render(
            "ENTER o ESC para volver al menú",
            True,
            COLOR_TEXTO,
        )
        pantalla.blit(
            ayuda,
            (ANCHO_VENTANA // 2 - ayuda.get_width() // 2, ALTO_VENTANA - 60),
        )

        pygame.display.flip()
        reloj.tick(60)
