# src/puntuacion.py

PUNTOS_BASE_ESCAPA = 1000.0
BONO_POR_TRAMPA = 15          # bono por enemigo eliminado con trampa
PUNTOS_ENEMIGO_ESCAPADO = 50  # en modo cazador


def calcular_puntaje_escapa(
    duracion_segundos: float,
    num_enemigos: int,
    factor_dificultad: float,
    enemigos_eliminados_trampa: int = 0,
) -> int:
    """
    Menor tiempo -> más puntos.
    Más enemigos / más dificultad -> más puntos.
    Cada enemigo eliminado con trampa da un bono fijo.
    """
    if duracion_segundos <= 0:
        duracion_segundos = 0.1

    dificultad_total = max(1.0, num_enemigos * factor_dificultad)
    base = PUNTOS_BASE_ESCAPA * dificultad_total / duracion_segundos
    bono_trampas = enemigos_eliminados_trampa * BONO_POR_TRAMPA

    return int(round(base + bono_trampas))


def calcular_puntaje_cazador(
    enemigos_atrapados: int,
    enemigos_escapados: int,
) -> int:
    """
    Si un enemigo escapa pierdes X puntos.
    Si lo atrapas antes de que escape, ganas el doble de X.
    """
    return (2 * PUNTOS_ENEMIGO_ESCAPADO * enemigos_atrapados
            - PUNTOS_ENEMIGO_ESCAPADO * enemigos_escapados)
