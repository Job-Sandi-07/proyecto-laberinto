import os
import pygame


RUTA_MUSICA = os.path.join(os.path.dirname(__file__), "music.mp3")


def iniciar_musica(loop: bool = True, volumen: float = 0.5) -> None:
  
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        if pygame.mixer.music.get_busy():
            pygame.mixer.music.set_volume(volumen)
            return

        pygame.mixer.music.load(RUTA_MUSICA)
        pygame.mixer.music.set_volume(volumen)
        pygame.mixer.music.play(-1 if loop else 0)
    except pygame.error as e:
        print(f"[MUSICA] No se pudo reproducir {RUTA_MUSICA}: {e}")


def detener_musica() -> None:
    if pygame.mixer.get_init():
        pygame.mixer.music.stop()
