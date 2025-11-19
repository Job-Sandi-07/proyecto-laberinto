from typing import Tuple

class Jugador:
    """
    Representa al jugador.

    - Tiene energía para correr.
    - Caminando: 1 casilla por turno.
    - Corriendo: 2 casillas por turno (más rápido que los enemigos).
    """

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

        self.energia_max = 100
        self.energia = self.energia_max

        self.corriendo: bool = False

        # Velocidades
        self.velocidad_caminar = 1
        self.velocidad_correr = 2  # => el jugador será más rápido que los enemigos

        # Costos / recuperación de energía
        self.costo_correr_por_paso = 8      # energía gastada por cada casilla corriendo
        self.recuperacion_por_turno = 3     # energía recuperada cuando camina

    # ---------- utilidades ----------

    def posicion(self) -> Tuple[int, int]:
        return self.x, self.y

    def _velocidad_actual(self) -> int:
        return self.velocidad_correr if self.corriendo else self.velocidad_caminar

    def obtener_barra_energia(self) -> str:
        longitud_barra = 20
        ratio = self.energia / self.energia_max
        llenas = int(longitud_barra * ratio)
        vacias = longitud_barra - llenas

        estado = "corriendo" if self.corriendo else "caminando"
        barra = f"[{'#' * llenas}{'.' * vacias}] {self.energia}/{self.energia_max} ({estado})"
        return barra

    # ---------- control de correr ----------

    def iniciar_correr(self) -> bool:
        """
        Intenta activar el modo correr.
        Devuelve True si pudo (tenía energía) o False si no.
        """
        if self.energia <= 0:
            return False
        self.corriendo = True
        return True

    def detener_correr(self) -> None:
        self.corriendo = False

    # ---------- movimiento ----------

    def mover(self, dx: int, dy: int, mapa) -> bool:
        """
        Mueve al jugador en la dirección (dx, dy), respetando el mapa.
        Si está corriendo, intenta avanzar 2 casillas en esa dirección.
        Devuelve True si se movió al menos una casilla.
        """
        if dx == 0 and dy == 0:
            return False

        pasos = self._velocidad_actual()
        se_movio = False

        for _ in range(pasos):
            nuevo_x = self.x + dx
            nuevo_y = self.y + dy

            # Verificamos si la casilla es transitable para el jugador
            if not mapa.es_transitable_por_jugador(nuevo_x, nuevo_y):
                # Si choca con un muro / casilla no transitable, dejamos de avanzar
                break

            # Movimiento válido
            self.x, self.y = nuevo_x, nuevo_y
            se_movio = True

            # Si está corriendo, gastar energía por cada paso
            if self.corriendo:
                self.energia = max(0, self.energia - self.costo_correr_por_paso)
                if self.energia == 0:
                    # Se quedó sin energía: deja de correr
                    self.corriendo = False
                    break

        # Recuperar energía cuando se movió caminando (no corriendo)
        if se_movio and not self.corriendo:
            self.energia = min(self.energia_max, self.energia + self.recuperacion_por_turno)

        return se_movio
