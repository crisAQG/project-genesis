import heapq
import random
from pygame.math import Vector2


class Entity:

    def __init__(self, worldx, worldy, size, scale, color, is_flying=False):
        self.position = Vector2(worldx, worldy)
        self.size = size
        self.scale = scale
        self.color = color
        self.is_flying = is_flying

        # IA
        self.priorities = []

        # Patrulla aleatoria
        self.patrol_target = None
        self.patrol_path = []
        self.patrol_path_index = 0

    # ==========================================================
    # MOVIMIENTO
    # ==========================================================

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

    def random_patrol(self, is_walkable, patrol_radius, speed, game, tile_size=1):
        """
        Patrulla aleatoriamente alrededor de la entidad usando A*, SIN
        depender de un tamaño de mundo fijo -map_width/map_height ya
        no existen-: el destino se busca dentro de "patrol_radius"
        tiles alrededor de la POSICIÓN ACTUAL de la entidad, así que
        funciona igual de bien cerca del (0, 0) que a millones de
        tiles de distancia, como corresponde a un mundo infinito
        generado por chunks (map_gen.py).

        is_walkable(tile_x, tile_y):
            Debe devolver True si la celda -en coordenadas de TILE, no
            de píxeles- se puede atravesar. Si tu mapa expone
            is_walkable en píxeles (como map_gen.is_walkable), pasale
            el wrapper en tiles (map_gen.is_walkable_tile).

        patrol_radius:
            Radio de búsqueda en tiles alrededor de la posición actual
            para elegir el próximo destino de patrulla.

        speed:
            Velocidad de movimiento en píxeles/frame.

        tile_size:
            Tamaño de un tile en píxeles, para convertir entre la
            posición de mundo (en píxeles) de la entidad y las
            coordenadas de grid (en tiles) que usan is_walkable y A*.
            Dejalo en 1 si tu mundo ya trabaja 1:1 en píxeles.

        La entidad:
            1. Elige una celda caminable dentro del radio.
            2. Calcula un camino mediante A*.
            3. Sigue el camino.
            4. Al llegar, elige otro destino.
        """
        if game.ahora - game.inicio <=6000:
            # Si no tenemos destino, buscar uno
            if self.patrol_target is None:

                origin = self.get_grid_position(tile_size)

                self.patrol_target = self.get_random_walkable_position(
                    is_walkable,
                    origin,
                    patrol_radius
                )

                if self.patrol_target is None:
                    return

                self.patrol_path = self.find_path(
                    origin,
                    self.patrol_target,
                    is_walkable
                )

                self.patrol_path_index = 0

            # Si no encontramos camino, buscar otro destino
            if not self.patrol_path:
                self.patrol_target = None
                return

            # Si llegamos al final del camino
            if self.patrol_path_index >= len(self.patrol_path):
                self.patrol_target = None
                self.patrol_path = []
                self.patrol_path_index = 0
                return

            # Siguiente celda (en tiles) -> posición de mundo (en píxeles)
            target_cell = self.patrol_path[self.patrol_path_index]

            target_position = Vector2(
                target_cell[0] * tile_size,
                target_cell[1] * tile_size
            )

            direction = target_position - self.position
            distance = direction.length()

            # Llegamos a la celda
            if distance <= speed:
                self.position = target_position
                self.patrol_path_index += 1
                return

            # Movernos hacia la celda
            if distance > 0:
                self.position += direction.normalize() * speed

        if game.ahora - game.inicio >= 11000:
            game.inicio = game.ahora

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