from typing import Tuple, Optional

from src.mapa.mapa import Mapa


# Constantes para el modo de juego
MODO_ESCAPA = "escapa"
MODO_CAZADOR = "cazador"


class Enemigo:
    """
    Representa un cazador.

    - En modo ESCAPA: persigue al jugador.
    - En modo CAZADOR: huye del jugador.
    - Se mueve en 4 direcciones y respeta Mapa.es_transitable_por_enemigo().
    """

    def __init__(self, x: int, y: int, velocidad_celdas_por_turno: int = 1):
        self.x = x
        self.y = y
        self.velocidad_celdas_por_turno = velocidad_celdas_por_turno

        self.vivo: bool = True
        self.tiempo_muerte: Optional[float] = None  # para respawn luego

    # ------------ Propiedades útiles ------------

    @property
    def posicion(self) -> Tuple[int, int]:
        return self.x, self.y

    # ------------ Lógica principal ------------

    def actualizar(
        self,
        mapa: Mapa,
        posicion_jugador: Tuple[int, int],
        modo: str,
    ) -> None:
        """
        Mueve al enemigo UNA casilla según el modo y la posición del jugador.
        Llama a este método en cada 'tick' del juego.
        """
        if not self.vivo:
            return

        dx, dy = self._calcular_paso(mapa, posicion_jugador, modo)
        if dx == 0 and dy == 0:
            return  # no hay movimiento posible

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
        """
        Decide hacia dónde moverse:
        - ESCAPA: elige la casilla que ACERCA al jugador (perseguir).
        - CAZADOR: elige la casilla que ALEJA del jugador (huir).
        Siempre respeta el mapa.
        """
        jugador_x, jugador_y = posicion_jugador

        # Las 4 direcciones posibles: arriba, abajo, izquierda, derecha
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
            # Rodeado de muros / casillas no transitables
            return 0, 0

        # En ESCAPA: queremos disminuir la distancia → orden ascendente.
        # En CAZADOR: queremos aumentar la distancia → orden descendente.
        reverse = (modo == MODO_CAZADOR)
        candidatos.sort(key=lambda item: item[1], reverse=reverse)

        mejor_movimiento, _ = candidatos[0]
        return mejor_movimiento

    # ------------ Muerte y respawn (para usar con trampas) ------------

    def matar(self, tiempo_actual: float) -> None:
        """
        Marca al enemigo como muerto. No se moverá hasta respawn.
        """
        self.vivo = False
        self.tiempo_muerte = tiempo_actual

    def listo_para_respawn(self, tiempo_actual: float, delay: float) -> bool:
        """
        Devuelve True si han pasado 'delay' segundos desde que murió.
        (El juego decidirá dónde reaparecerlo.)
        """
        if not self.vivo and self.tiempo_muerte is not None:
            return (tiempo_actual - self.tiempo_muerte) >= delay
        return False

    def respawnear(self, nueva_posicion: Tuple[int, int]) -> None:
        """
        Reactiva al enemigo en una nueva posición.
        """
        self.x, self.y = nueva_posicion
        self.vivo = True
        self.tiempo_muerte = None
