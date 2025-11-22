# src/puntuacion.py

import json
import os
from typing import Dict, List


# -----------------------------
#  Parte 1: cálculo de puntajes
# -----------------------------

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


# ------------------------------------
#  Parte 2: almacenamiento de Top 5
# ------------------------------------

# El JSON se guardará junto a este archivo
RUTA_PUNTAJES = os.path.join(os.path.dirname(__file__), "puntajes.json")


def _estructura_vacia() -> Dict[str, List[Dict[str, int]]]:
    return {
        "escapa": [],
        "cazador": [],
    }


def cargar_puntajes() -> Dict[str, List[Dict[str, int]]]:
    if not os.path.exists(RUTA_PUNTAJES):
        return _estructura_vacia()

    try:
        with open(RUTA_PUNTAJES, "r", encoding="utf-8") as f:
            datos = json.load(f)
        # Asegurar claves
        if "escapa" not in datos:
            datos["escapa"] = []
        if "cazador" not in datos:
            datos["cazador"] = []
        return datos
    except (json.JSONDecodeError, OSError):
        # Si el archivo está corrupto, empezamos de cero
        return _estructura_vacia()


def guardar_puntajes(datos: Dict[str, List[Dict[str, int]]]) -> None:
    with open(RUTA_PUNTAJES, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)


def _clave_desde_modo(modo: str) -> str:
    """
    Recibe el modo como string (por ejemplo 'ESCAPA' o 'CAZADOR')
    y devuelve la clave interna ('escapa' o 'cazador').
    No importamos src.entidades para evitar imports circulares.
    """
    modo_upper = (modo or "").upper()
    if "ESCAPA" in modo_upper:
        return "escapa"
    if "CAZADOR" in modo_upper:
        return "cazador"
    # por defecto
    return "escapa"


def registrar_puntaje(modo: str, nombre: str, puntaje: int) -> None:
    """
    Agrega un puntaje al Top 5 del modo dado (Escapa o Cazador).
    Mantiene solo los 5 mejores puntajes.
    """
    datos = cargar_puntajes()

    clave = _clave_desde_modo(modo)
    lista = datos.get(clave, [])
    lista.append({"nombre": nombre, "puntaje": int(puntaje)})

    # Ordenar de mayor a menor puntaje y limitar a 5
    lista.sort(key=lambda x: x["puntaje"], reverse=True)
    datos[clave] = lista[:5]

    guardar_puntajes(datos)


def obtener_top5(modo: str) -> List[Dict[str, int]]:
    """
    Devuelve la lista Top 5 del modo dado.
    Cada elemento es un dict: {"nombre": str, "puntaje": int}
    """
    datos = cargar_puntajes()
    clave = _clave_desde_modo(modo)
    return datos.get(clave, [])
