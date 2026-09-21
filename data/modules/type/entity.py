import heapq
import random
import pygame
from pygame.math import Vector2
from data.modules.services.spr_manager import spr_manager


class Entity:

    def __init__(self, worldx, worldy, size, scale, hp, speed, dmg, shield, color, spr, sx, sy, is_flying=False):
        self.position = Vector2(worldx, worldy)
        self.size = size
        self.scale = scale
        self.color = color
        self.is_flying = is_flying

        self.velocity = Vector2(0, 0)
        self.angle = 0
        self.rotation_speed = 5

        # Stats
        self.hp = hp
        self.speed = speed
        self.dmg = dmg
        self.shield = shield

        # IA
        self.priorities = []

        self.patrol_target = None
        self.patrol_path = []
        self.patrol_path_index = 0
        self._patrol_cycle_start = None

        try:
            self.original_image = spr_manager(spr).get_sprite(sx, sy, self.size, self.size)
            self.original_image = pygame.transform.scale(self.original_image, (self.size, self.size))
            self.active_sprite = True
        except Exception as e:
            print(f"⚠️ Entity: no pude cargar sprite '{spr}', uso un color de relleno ({e})")
            self.original_image = pygame.Surface((self.size, self.size))
            self.original_image.fill(color)
            self.active_sprite = False

        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(topleft=(self.position.x, self.position.y))

    # ==========================================================
    # MOVIMIENTO
    # ==========================================================

    def rotate(self, direction):
        if direction.length_squared() == 0:
            return

        target_angle = direction.angle_to(Vector2(1, 0))-90

        angle_diff = (target_angle - self.angle) % 360

        if angle_diff > 180:
            angle_diff -= 360

        if abs(angle_diff) < self.rotation_speed:
            self.angle = target_angle
        else:
            self.angle += self.rotation_speed if angle_diff > 0 else -self.rotation_speed

        self.angle %= 360

        self.image = pygame.transform.rotate(
            self.original_image,
            self.angle
        )

        self.rect = self.image.get_rect(center=self.rect.center)

    @staticmethod
    def chase_target(entity_pos, target_pos, speed):
        """Mueve una entidad hacia un objetivo."""

        direction = Vector2(target_pos) - Vector2(entity_pos)
        distance = direction.length()

        if distance == 0:
            return Vector2(entity_pos)

        # Evita sobrepasar el objetivo
        if distance <= speed:
            return Vector2(target_pos)

        return Vector2(entity_pos) + direction.normalize() * speed

    @staticmethod
    def flee_target(entity_pos, threat_pos, speed):
        """Mueve una entidad alejándose de una amenaza."""

        direction = Vector2(entity_pos) - Vector2(threat_pos)
        distance = direction.length()

        if distance == 0:
            return Vector2(entity_pos)

        return Vector2(entity_pos) + direction.normalize() * speed

    # ==========================================================
    # PATRULLA NORMAL
    # ==========================================================

    @staticmethod
    def patrol(waypoints, current_index, position, speed):
        """
        Sigue una lista de waypoints en bucle.

        Returns:
            (nueva_posicion, nuevo_indice)
        """

        if not waypoints:
            return Vector2(position), current_index

        position = Vector2(position)
        target = Vector2(waypoints[current_index])

        direction = target - position
        distance = direction.length()

        # Llegamos al waypoint
        if distance <= speed:
            position = target
            current_index = (current_index + 1) % len(waypoints)
            return position, current_index

        position += direction.normalize() * speed

        return position, current_index

    # ==========================================================
    # PATRULLA ALEATORIA (mundo infinito)
    # ==========================================================

    def random_patrol(self, game, patrol_radius=10, tile_size=1,
                       active_duration=6000, cycle_duration=11000):
        """
        Patrulla en ciclos alrededor de la posición actual, usando A*,
        SIN depender de un tamaño de mundo fijo -el destino se busca
        dentro de "patrol_radius" tiles alrededor de donde está la
        entidad AHORA, así que funciona igual cerca del (0,0) que a
        millones de tiles de distancia-.

        Cada ciclo dura "cycle_duration" ms: durante los primeros
        "active_duration" ms la entidad busca destino y lo persigue
        con A*; el resto del ciclo queda quieta. Al pasar
        "cycle_duration" arranca un ciclo nuevo con un destino nuevo.
        El reloj del ciclo es un atributo PROPIO de la entidad
        (self._patrol_cycle_start) -si lo guardás en el objeto game
        compartido, dos entidades patrullando se resetean el ciclo
        una a la otra-.

        game:
            Necesita exponer:
              - game.ahora: el reloj del juego en ms (mismo que uses
                en el resto del loop).
              - game.world.is_walkable_tile(tile_x, tile_y): callback
                de caminable en coordenadas de TILE (no píxeles). Si
                tu mundo expone is_walkable en píxeles, usá el wrapper
                (map_gen.is_walkable_tile ya existe para esto).

        patrol_radius:
            Radio de búsqueda en tiles alrededor de la posición actual
            para elegir destino.

        tile_size:
            Tamaño de un tile en píxeles, para convertir entre la
            posición de mundo (píxeles) de la entidad y las
            coordenadas de grid (tiles) que usan is_walkable y A*.
            Dejalo en 1 si tu mundo ya trabaja 1:1 en píxeles.

        La entidad, cada ciclo:
            1. Elige una celda caminable dentro del radio.
            2. Calcula un camino mediante A*.
            3. Sigue el camino (rotando hacia donde avanza).
            4. Al llegar, o al pasarse de active_duration, se detiene
               hasta el próximo ciclo.
        """
        if self._patrol_cycle_start is None:
            self._patrol_cycle_start = game.ahora

        elapsed = game.ahora - self._patrol_cycle_start

        # Ciclo terminado: arrancar uno nuevo (destino/camino nuevos)
        if elapsed >= cycle_duration:
            self._patrol_cycle_start = game.ahora
            self.patrol_target = None
            self.patrol_path = []
            self.patrol_path_index = 0
            return

        # Fuera de la ventana activa: quieta hasta el próximo ciclo
        if elapsed > active_duration:
            return

        is_walkable = game.world.is_walkable_tile

        # Sin destino todavía: elegir uno y calcular el camino
        if self.patrol_target is None:
            origin = self.get_grid_position(tile_size)

            self.patrol_target = self.get_random_walkable_position(
                is_walkable,
                origin,
                patrol_radius
            )

            if self.patrol_target is None:
                return  # no encontró celda caminable cerca; probará el próximo ciclo

            self.patrol_path = self.find_path(
                origin,
                self.patrol_target,
                is_walkable
            )

            self.patrol_path_index = 0

        # A* no encontró camino hasta el destino
        if not self.patrol_path:
            self.patrol_target = None
            return

        # Ya recorrió todo el camino: esperar al próximo ciclo
        if self.patrol_path_index >= len(self.patrol_path):
            return

        # Siguiente celda del camino
        target_cell = self.patrol_path[self.patrol_path_index]

        target_position = Vector2(
            target_cell[0] * tile_size,
            target_cell[1] * tile_size
        )

        direction = target_position - self.position
        distance = direction.length()

        # Ya estamos en la celda
        if distance == 0:
            self.patrol_path_index += 1
            return

        direction = direction.normalize()

        # Rotar hacia donde se mueve
        self.rotate(direction)

        # Avanzar
        if distance <= self.speed:
            self.position = target_position
            self.patrol_path_index += 1
        else:
            self.position += direction * self.speed

        # Sincronizar el rect con la posición -sin esto, la entidad se
        # mueve "de verdad" (self.position) pero se dibuja siempre en
        # el mismo lugar, porque nada más toca self.rect.center-.
        self.rect.center = self.position

    # ==========================================================
    # UTILIDADES DE PATRULLA
    # ==========================================================

    def get_grid_position(self, tile_size=1):
        """
        Convierte la posición de mundo (píxeles) a coordenadas de grid
        (tile). Con tile_size=1 (default) se comporta igual que antes,
        en píxeles; pasale el tile_size real de tu mapa (32, por
        ejemplo) para que la patrulla y el A* trabajen sobre tiles en
        vez de sobre píxeles sueltos.
        """

        return (
            round(self.position.x / tile_size),
            round(self.position.y / tile_size)
        )

    @staticmethod
    def get_random_walkable_position(is_walkable, origin, radius, max_attempts=100):
        """
        Busca una celda caminable dentro de "radius" tiles alrededor de
        "origin" (tile_x, tile_y). A diferencia de la versión anterior
        -que elegía con random.randrange(map_width)/(map_height), es
        decir dentro de un rectángulo [0, map_width) x [0, map_height)
        fijo-, esta busca siempre RELATIVO a dónde está la entidad, sin
        ningún límite de mundo. Por eso sirve para un mundo infinito
        generado por chunks: no existe un "map_width" que darle.
        """

        ox, oy = origin

        for _ in range(max_attempts):

            x = ox + random.randint(-radius, radius)
            y = oy + random.randint(-radius, radius)

            if is_walkable(x, y):
                return x, y

        return None

    # ==========================================================
    # VISIÓN
    # ==========================================================

    @staticmethod
    def can_see(pos_a, pos_b, max_distance):
        """Comprueba si dos posiciones están dentro del rango de visión."""

        dx = pos_b[0] - pos_a[0]
        dy = pos_b[1] - pos_a[1]

        return (dx ** 2 + dy ** 2) <= max_distance ** 2

    # ==========================================================
    # TARGETS
    # ==========================================================

    @staticmethod
    def select_target(priorities, visible_targets):
        """
        Selecciona el objetivo visible con mayor prioridad.

        visible_targets:
            [
                ("player", datos),
                ("enemy", datos),
                ...
            ]
        """

        for priority in priorities:
            for target in visible_targets:
                if target[0] == priority:
                    return target

        return None

    def update_priorities(self, new_priorities):
        """Actualiza las prioridades de la IA."""

        self.priorities = list(new_priorities)

    # ==========================================================
    # A*
    # ==========================================================

    @staticmethod
    def heuristic(a, b):
        """Distancia Manhattan."""

        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    @staticmethod
    def get_neighbors(is_walkable, node):
        """
        Obtiene las celdas adyacentes caminables (en coordenadas de
        TILE: +/-1 significa "el tile de al lado", no un píxel).
        """

        x, y = node

        neighbors = [
            (x + 1, y),
            (x - 1, y),
            (x, y + 1),
            (x, y - 1)
        ]

        return [
            neighbor
            for neighbor in neighbors
            if is_walkable(neighbor[0], neighbor[1])
        ]

    @staticmethod
    def reconstruct_path(came_from, current):
        """Reconstruye el camino encontrado por A*."""

        path = [current]

        while current in came_from:
            current = came_from[current]
            path.append(current)

        path.reverse()

        return path

    @staticmethod
    def find_path(start, goal, is_walkable):
        """
        Algoritmo A*.

        Args:
            start: (tile_x, tile_y)
            goal: (tile_x, tile_y)
            is_walkable: función que determina si una celda (en tiles)
                es transitable.

        Returns:
            Lista de posiciones (en tiles) o None.
        """

        if not is_walkable(start[0], start[1]):
            return None

        if not is_walkable(goal[0], goal[1]):
            return None

        open_set = []

        heapq.heappush(
            open_set,
            (0, start)
        )

        came_from = {}

        g_score = {
            start: 0
        }

        f_score = {
            start: Entity.heuristic(start, goal)
        }

        while open_set:

            _, current = heapq.heappop(open_set)

            # Llegamos al objetivo
            if current == goal:
                return Entity.reconstruct_path(
                    came_from,
                    current
                )

            for neighbor in Entity.get_neighbors(
                is_walkable,
                current
            ):

                tentative_g = g_score[current] + 1

                if (
                    neighbor not in g_score
                    or tentative_g < g_score[neighbor]
                ):

                    came_from[neighbor] = current

                    g_score[neighbor] = tentative_g

                    f_score[neighbor] = (
                        tentative_g
                        + Entity.heuristic(neighbor, goal)
                    )

                    heapq.heappush(
                        open_set,
                        (
                            f_score[neighbor],
                            neighbor
                        )
                    )

        return None