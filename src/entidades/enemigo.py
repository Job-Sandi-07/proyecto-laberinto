from typing import Tuple, Optional

from src.mapa.mapa import Mapa


MODO_ESCAPA = "escapa"
MODO_CAZADOR = "cazador"


class Enemigo:
    """
    Representa un cazador.

    - En modo ESCAPA: persigue al jugador.
    - En modo CAZADOR: huye del jugador.
    """

    def __init__(self, x: int, y: int, velocidad_celdas_por_turno: int = 1):
        self.x = x
        self.y = y
        self.velocidad_celdas_por_turno = velocidad_celdas_por_turno

        self.vivo: bool = True
        self.tiempo_muerte: Optional[float] = None

    @property
    def posicion(self) -> Tuple[int, int]:
        return self.x, self.y

    def actualizar(
        self,
        mapa: Mapa,
        posicion_jugador: Tuple[int, int],
        modo: str,
    ) -> None:
        if not self.vivo:
            return

        dx, dy = self._calcular_paso(mapa, posicion_jugador, modo)
        if dx == 0 and dy == 0:
            return

        nuevo_x = self.x + dx
        nuevo_y = self.y + dy

        if mapa.es_transitable_por_enemigo(nuevo_x, nuevo_y):
            self.x = nuevo_x
            self.y = nuevo_y

    def _calcular_paso(
        self,
        mapa: Mapa,
        posicion_jugador: Tuple[int, int],
        modo: str,
    ) -> Tuple[int, int]:
        jugador_x, jugador_y = posicion_jugador

        direcciones = [
            (0, -1),
            (0, 1),
            (-1, 0),
            (1, 0),
        ]

        candidatos = []

        def distancia_manhattan(x: int, y: int) -> int:
            return abs(x - jugador_x) + abs(y - jugador_y)

        for dx, dy in direcciones:
            nx = self.x + dx
            ny = self.y + dy

            if not mapa.dentro_limites(nx, ny):
                continue
            if not mapa.es_transitable_por_enemigo(nx, ny):
                continue

            d = distancia_manhattan(nx, ny)
            candidatos.append(((dx, dy), d))

        if not candidatos:
            return 0, 0

        reverse = (modo == MODO_CAZADOR)
        candidatos.sort(key=lambda item: item[1], reverse=reverse)

        mejor_movimiento, _ = candidatos[0]
        return mejor_movimiento

    def matar(self, tiempo_actual: float) -> None:
        self.vivo = False
        self.tiempo_muerte = tiempo_actual

    def listo_para_respawn(self, tiempo_actual: float, delay: float) -> bool:
        if not self.vivo and self.tiempo_muerte is not None:
            return (tiempo_actual - self.tiempo_muerte) >= delay
        return False

    def respawnear(self, nueva_posicion: Tuple[int, int]) -> None:
        self.x, self.y = nueva_posicion
        self.vivo = True
        self.tiempo_muerte = None
