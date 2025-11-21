from typing import Optional, Tuple

from .enemigo import Enemigo


class Trampa:
    SIMBOLO_TEXTO = "X"

    def __init__(self, x: int, y: int, tiempo_colocacion: float) -> None:
        self.x = x
        self.y = y
        self.tiempo_colocacion = tiempo_colocacion
        self.activa: bool = True
        self.tiempo_uso: Optional[float] = None
    def posicion(self) -> Tuple[int, int]:
        return self.x, self.y

    def esta_activa(self) -> bool:
        return self.activa

    def desactivar(self, tiempo_actual: Optional[float] = None) -> None:
        self.activa = False
        if tiempo_actual is not None:
            self.tiempo_uso = tiempo_actual

    def activar_si_enemigo_pisa(self, enemigo: Enemigo, tiempo_actual: float) -> bool:
        if not self.activa or not enemigo.vivo:
            return False

        if enemigo.posicion != self.posicion:
            return False

        enemigo.matar(tiempo_actual)
        self.activa = False
        self.tiempo_uso = tiempo_actual
        return True