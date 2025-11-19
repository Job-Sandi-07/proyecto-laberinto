from __future__ import annotations
from dataclasses import dataclass

from src.mapa.mapa import Mapa


@dataclass
class Jugador:
    x: int
    y: int
    energia_maxima: int = 100
    energia_actual: int = 100
    costo_correr: int = 10       # energía que gasta por movimiento corriendo
    regeneracion: int = 3        # energía que recupera por movimiento caminando
    corriendo: bool = False

    def posicion(self) -> tuple[int, int]:
        return self.x, self.y

    def puede_correr(self) -> bool:
        """Revisa si tiene energía suficiente para correr."""
        return self.energia_actual >= self.costo_correr

    def iniciar_correr(self) -> bool:
        """
        Intenta activar el modo correr.
        Devuelve True si lo logró, False si no había energía.
        """
        if self.puede_correr():
            self.corriendo = True
            return True
        return False

    def detener_correr(self) -> None:
        self.corriendo = False

    def mover(self, dx: int, dy: int, mapa: Mapa) -> bool:
        """
        Intenta mover al jugador en la dirección (dx, dy).
        Devuelve True si se movió, False si la casilla no era transitable.
        """
        nuevo_x = self.x + dx
        nuevo_y = self.y + dy

        if not mapa.es_transitable_por_jugador(nuevo_x, nuevo_y):
            # No puede pasar (muro o fuera de mapa)
            return False

        # Movimiento válido
        self.x = nuevo_x
        self.y = nuevo_y

        # Actualizamos energía en función de si está corriendo o no
        self._aplicar_energia_por_movimiento()
        return True

    def _aplicar_energia_por_movimiento(self) -> None:
        """Lógica de gasto / recuperación de energía por cada movimiento."""
        if self.corriendo and self.puede_correr():
            # Gasta energía por correr
            self.energia_actual -= self.costo_correr
            if self.energia_actual < 0:
                self.energia_actual = 0
        else:
            # Regenera energía (caminando o sin energía para correr)
            self.corriendo = False  # si no puede correr, se apaga el modo
            self.energia_actual += self.regeneracion
            if self.energia_actual > self.energia_maxima:
                self.energia_actual = self.energia_maxima

    def obtener_barra_energia(self, longitud: int = 20) -> str:
        """
        Devuelve una barra de energía tipo:
        [##########----------] 50/100
        """
        ratio = self.energia_actual / self.energia_maxima
        llenos = int(ratio * longitud)
        vacios = longitud - llenos
        barra = "[" + "#" * llenos + "-" * vacios + "]"
        return f"{barra} {self.energia_actual}/{self.energia_maxima} ({'CORRIENDO' if self.corriendo else 'caminando'})"
