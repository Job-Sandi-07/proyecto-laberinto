import pygame
import sys

ANCHO_VENTANA = 600
ALTO_VENTANA = 200
COLOR_FONDO = (0, 0, 0)
COLOR_TEXTO = (255, 255, 255)
COLOR_CAJA = (50, 50, 50)


def pedir_nombre() -> str:
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
    pygame.display.set_caption("Registro de jugador")

    fuente = pygame.font.SysFont(None, 32)
    reloj = pygame.time.Clock()

    nombre = ""
    terminado = False

    while not terminado:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)   # cerrar TODO

            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    if nombre.strip():
                        terminado = True
                elif evento.key == pygame.K_BACKSPACE:
                    nombre = nombre[:-1]
                else:
                    nombre += evento.unicode

        # Dibujar
        pantalla.fill(COLOR_FONDO)

        texto_titulo = fuente.render(
            "Escribe tu nombre y presiona ENTER", True, COLOR_TEXTO
        )
        pantalla.blit(texto_titulo, (20, 40))

        caja_rect = pygame.Rect(20, 90, ANCHO_VENTANA - 40, 40)
        pygame.draw.rect(pantalla, COLOR_CAJA, caja_rect)

        texto_nombre = fuente.render(nombre, True, COLOR_TEXTO)
        pantalla.blit(texto_nombre, (caja_rect.x + 10, caja_rect.y + 8))

        pygame.display.flip()
        reloj.tick(30)

    pygame.quit()

    nombre_final = nombre.strip()
    if not nombre_final:
        nombre_final = "Jugador"

    return nombre_final
