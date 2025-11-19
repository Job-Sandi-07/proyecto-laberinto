from abc import ABC, abstractmethod


# Códigos numéricos que usaremos en la matriz
COD_CAMINO = 0
COD_MURO = 1
COD_TUNEL = 2
COD_LIANA = 3


class Casilla(ABC):
    """
    Clase base para cualquier casilla del mapa.
    """

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    @property
    @abstractmethod
    def codigo(self) -> int:
        """Código numérico de esta casilla en la matriz."""
        ...

    @property
    @abstractmethod
    def simbolo(self) -> str:
        """Carácter para mostrar la casilla en texto (para debug)."""
        ...

    def es_transitable_por_jugador(self) -> bool:
        """Por defecto, sí es transitable. Las subclases pueden cambiar esto."""
        return True

    def es_transitable_por_enemigo(self) -> bool:
        """Por defecto, sí es transitable. Las subclases pueden cambiar esto."""
        return True


class Camino(Casilla):
    @property
    def codigo(self) -> int:
        return COD_CAMINO

    @property
    def simbolo(self) -> str:
        return " "  # espacio vacío


class Muro(Casilla):
    @property
    def codigo(self) -> int:
        return COD_MURO

    @property
    def simbolo(self) -> str:
        return "#"

    def es_transitable_por_jugador(self) -> bool:
        return False

    def es_transitable_por_enemigo(self) -> bool:
        return False


class Tunel(Casilla):
    """
    Túnel: solo el JUGADOR puede pasar; los cazadores NO.
    """

    @property
    def codigo(self) -> int:
        return COD_TUNEL

    @property
    def simbolo(self) -> str:
        return "T"

    def es_transitable_por_jugador(self) -> bool:
        return True

    def es_transitable_por_enemigo(self) -> bool:
        return False


class Liana(Casilla):
    """
    Liana: solo los CAZADORES pueden pasar; para el jugador es un obstáculo.
    """

    @property
    def codigo(self) -> int:
        return COD_LIANA

    @property
    def simbolo(self) -> str:
        return "L"

    def es_transitable_por_jugador(self) -> bool:
        return False

    def es_transitable_por_enemigo(self) -> bool:
        return True


def crear_casilla_desde_codigo(x: int, y: int, codigo: int) -> Casilla:
    """
    Fábrica de casillas a partir del valor numérico de la matriz.
    """
    if codigo == COD_CAMINO:
        return Camino(x, y)
    elif codigo == COD_MURO:
        return Muro(x, y)
    elif codigo == COD_TUNEL:
        return Tunel(x, y)
    elif codigo == COD_LIANA:
        return Liana(x, y)
    else:
        raise ValueError(f"Código de casilla desconocido: {codigo}")
