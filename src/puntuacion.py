# src/puntuacion.py

PUNTOS_BASE_ESCAPA = 1000
PENALIZACION_POR_SEGUNDO = 5
BONO_POR_ENEMIGO = 50  # aumenta la recompensa por tener más enemigos / más difíciles

PUNTOS_ENEMIGO_ESCAPADO = -50
PUNTOS_ENEMIGO_ATRAPADO = 100  # el doble de lo que perderías si escapara


def calcular_puntaje_escapa(
    duracion_segundos: float,
    num_enemigos: int,
    factor_dificultad: float = 1.0,
) -> int:
    """
    Puntaje para modo Escapa:
    - Menos tiempo → más puntos.
    - Más enemigos / más dificultad → más puntos.
    """
    penalizacion_tiempo = int(duracion_segundos * PENALIZACION_POR_SEGUNDO)
    bono_enemigos = int(num_enemigos * BONO_POR_ENEMIGO * factor_dificultad)

    puntaje = PUNTOS_BASE_ESCAPA - penalizacion_tiempo + bono_enemigos
    return max(0, puntaje)


def calcular_puntaje_cazador(
    enemigos_atrapados: int,
    enemigos_escapados: int,
) -> int:
    """
    Puntaje para modo Cazador:
    - Cada enemigo atrapado suma.
    - Cada enemigo que llega a la salida resta.
    """
    return (
        enemigos_atrapados * PUNTOS_ENEMIGO_ATRAPADO
        + enemigos_escapados * PUNTOS_ENEMIGO_ESCAPADO
    )
