from typing import List, Tuple, Optional, Iterable

from .casillas import Casilla, crear_casilla_desde_codigo


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

    # ---------- utilidades básicas ----------

    def dentro_limites(self, x: int, y: int) -> bool:
        """
        Devuelve True si (x, y) está dentro del mapa.
        """
        return 0 <= x < self.ancho and 0 <= y < self.alto

    def obtener_casilla(self, x: int, y: int) -> Casilla:
        """
        Devuelve el objeto Casilla en la coordenada (x, y).
        Lanza IndexError si está fuera de límites.
        """
        if not self.dentro_limites(x, y):
            raise IndexError(f"Posición fuera de límites: ({x}, {y})")
        return self.casillas[y][x]

    def es_transitable_por_jugador(self, x: int, y: int) -> bool:
        """
        Indica si el jugador puede entrar en la casilla (x, y).
        """
        if not self.dentro_limites(x, y):
            return False
        return self.obtener_casilla(x, y).es_transitable_por_jugador()

    def es_transitable_por_enemigo(self, x: int, y: int) -> bool:
        """
        Indica si un enemigo puede entrar en la casilla (x, y).
        """
        if not self.dentro_limites(x, y):
            return False
        return self.obtener_casilla(x, y).es_transitable_por_enemigo()

    # ---------- debug en consola ----------

    def mostrar_en_consola(
        self,
        pos_jugador: Optional[Tuple[int, int]] = None,
        posiciones_enemigos: Optional[Iterable[Tuple[int, int]]] = None,
    ) -> None:
        """
        Muestra el mapa en texto. Muy útil para debug.
        J = jugador, E = enemigo, S = salida.
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
