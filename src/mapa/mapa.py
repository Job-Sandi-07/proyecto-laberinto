from typing import List, Tuple

from .casillas import (
    Casilla,
    crear_casilla_desde_codigo,
    COD_CAMINO,
    COD_MURO,
    COD_TUNEL,
    COD_LIANA,
)


class Mapa:
    """
    Envuelve la matriz de casillas y provee métodos de utilidad.
    """

    def __init__(
        self,
        casillas: List[List[Casilla]],
        inicio_jugador: Tuple[int, int],
        salida: Tuple[int, int],
    ):
        self.casillas = casillas
        self.alto = len(casillas)
        self.ancho = len(casillas[0]) if self.alto > 0 else 0
        self.inicio_jugador = inicio_jugador
        self.salida = salida

    @classmethod
    def desde_matriz(
        cls,
        matriz: List[List[int]],
        inicio_jugador: Tuple[int, int],
        salida: Tuple[int, int],
    ) -> "Mapa":
        """
        Construye un Mapa a partir de una matriz de códigos numéricos.
        """
        casillas: List[List[Casilla]] = []
        for y, fila in enumerate(matriz):
            fila_casillas: List[Casilla] = []
            for x, codigo in enumerate(fila):
                fila_casillas.append(crear_casilla_desde_codigo(x, y, codigo))
            casillas.append(fila_casillas)

        return cls(casillas, inicio_jugador, salida)

    def dentro_limites(self, x: int, y: int) -> bool:
        return 0 <= x < self.ancho and 0 <= y < self.alto

    def obtener_casilla(self, x: int, y: int) -> Casilla:
        if not self.dentro_limites(x, y):
            raise IndexError(f"Posición fuera de límites: ({x}, {y})")
        return self.casillas[y][x]

    def es_transitable_por_jugador(self, x: int, y: int) -> bool:
        if not self.dentro_limites(x, y):
            return False
        return self.obtener_casilla(x, y).es_transitable_por_jugador()

    def es_transitable_por_enemigo(self, x: int, y: int) -> bool:
        if not self.dentro_limites(x, y):
            return False
        return self.obtener_casilla(x, y).es_transitable_por_enemigo()

    def mostrar_en_consola(
        self,
        pos_jugador: Tuple[int, int] | None = None,
        posiciones_enemigos: list[Tuple[int, int]] | None = None,
    ) -> None:
        """
        Muestra el mapa en texto. Muy útil para debug en esta fase.
        """
        posiciones_enemigos = posiciones_enemigos or []
        enemigos_set = set(posiciones_enemigos)

        for y in range(self.alto):
            fila_str = ""
            for x in range(self.ancho):
                if pos_jugador == (x, y):
                    fila_str += "J"
                elif (x, y) in enemigos_set:
                    fila_str += "E"
                elif (x, y) == self.salida:
                    fila_str += "S"
                else:
                    fila_str += self.casillas[y][x].simbolo
            print(fila_str)
