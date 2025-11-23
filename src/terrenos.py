from __future__ import annotations

from typing import Tuple, List, Set
import random

from src.mapa.casillas import COD_CAMINO

# Conjuntos de posiciones especiales (x, y)
_TUNELES: Set[Tuple[int, int]] = set()
_LIANAS: Set[Tuple[int, int]] = set()


# ----------------------------------------------------------------------
# API pública para el resto del juego
# ----------------------------------------------------------------------
def agregar_terrenos_especiales(
    mapa,
    prob_tunel: float = 0.15,
    prob_liana: float = 0.15,
) -> None:
    """
    Elige algunas casillas de CAMINO del mapa y las marca como túneles
    o lianas (solo a nivel de coordenadas, no toca la casilla en sí).

    Probabilidades altas para que sean visibles; luego puedes bajarlas.
    """
    _TUNELES.clear()
    _LIANAS.clear()

    for y in range(mapa.alto):
        for x in range(mapa.ancho):
            # No tocar inicio ni salida
            if (x, y) == mapa.inicio_jugador or (x, y) == mapa.salida:
                continue

            casilla = mapa.obtener_casilla(x, y)
            if casilla.codigo != COD_CAMINO:
                continue

            r = random.random()
            if r < prob_tunel:
                _TUNELES.add((x, y))
            elif r < prob_tunel + prob_liana:
                _LIANAS.add((x, y))


def es_tunel(x: int, y: int) -> bool:
    return (x, y) in _TUNELES


def es_liana(x: int, y: int) -> bool:
    return (x, y) in _LIANAS


def aplicar_efecto_terreno_jugador(mapa, jugador) -> None:
    """
    Si el jugador está parado sobre un túnel o liana, aplica el efecto.
    """
    x, y = jugador.x, jugador.y

    if es_tunel(x, y):
        jugador.x, jugador.y = _usar_tunel(mapa, x, y)

    elif es_liana(x, y):
        jugador.x, jugador.y = _usar_liana(mapa, x, y, es_jugador=True)


def aplicar_efecto_terreno_enemigo(mapa, enemigo) -> None:
    """
    Si el enemigo está parado sobre un túnel o liana, aplica el efecto.
    """
    ex, ey = enemigo.posicion

    if es_tunel(ex, ey):
        nx, ny = _usar_tunel(mapa, ex, ey)
        enemigo.x, enemigo.y = nx, ny

    elif es_liana(ex, ey):
        nx, ny = _usar_liana(mapa, ex, ey, es_jugador=False)
        enemigo.x, enemigo.y = nx, ny


# ----------------------------------------------------------------------
# Helpers internos
# ----------------------------------------------------------------------
def _usar_tunel(mapa, x: int, y: int) -> Tuple[int, int]:
    tuneles = list(_TUNELES)
    if len(tuneles) <= 1:
        return x, y

    posibles = [p for p in tuneles if p != (x, y)]
    if not posibles:
        return x, y

    return random.choice(posibles)


def _usar_liana(mapa, x: int, y: int, es_jugador: bool) -> Tuple[int, int]:
    sx, sy = mapa.salida

    dx = 0
    dy = 0
    if sx > x:
        dx = 1
    elif sx < x:
        dx = -1
    if sy > y:
        dy = 1
    elif sy < y:
        dy = -1

    nx = x + dx
    ny = y + dy

    if es_jugador:
        es_ok = mapa.es_transitable_por_jugador(nx, ny)
    else:
        es_ok = mapa.es_transitable_por_enemigo(nx, ny)

    if es_ok:
        return nx, ny
    return x, y