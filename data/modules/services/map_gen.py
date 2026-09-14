import pygame, random, math, json

from data.modules.states.noise2 import noise2
from data.modules.services.spr_manager import spr_manager


tile_size = 32
height_range = [
    (0.32, "agua_profunda", (17, 63, 122), False, ""),
    (0.38, "agua", (31, 99, 173), False),
    (0.42, "arena", (231, 213, 158), True),
    (0.62, "pasto", (85, 158, 68), True),
    (0.83, "montania", (120, 114, 108), True),
    (0.9, "nieve", (240, 240, 245), True),
]

def height_map(h):
    for max_h, name, color, walkable in height_range:
        if h <= max_h:
            return name, color, walkable
    return height_range[-1][1], height_range[-1][2], height_range[-1][3]


class map_features:
    """
    Genera biomas (celdas tipo Voronoi/Worley) y ríos de forma
    DETERMINISTA a partir de la seed del mundo y la posición en
    tiles. No guarda estado que dependa del orden de generación de
    chunks: la celda Voronoi y el ruido de río de una posición dan
    siempre el mismo resultado, la calcules cuando la calcules, así
    que no hace falta persistir nada de esto en el save().

    IMPORTANTE sobre el rango de alturas: en tu height_range, "pasto"
    es 0.42 < h <= 0.62, y 0.62 es donde EMPIEZA "montania". Dejé
    BIOME_MIN_HEIGHT/BIOME_MAX_HEIGHT en (0.42, 0.62) para que caiga
    dentro de pasto. Si en realidad querías la franja de montaña
    (todo lo que es > 0.62), cambia estos dos valores a (0.62, 0.83).
    """

    BIOME_MIN_HEIGHT = 0.42
    BIOME_MAX_HEIGHT = 0.62

    VORONOI_CELL_SIZE = 96     # tamaño de celda en tiles; súbelo para biomas más grandes
    RIVER_FREQUENCY = 0.01     # más bajo = ríos más largos y suaves
    RIVER_WIDTH = 0.015        # más alto = ríos más anchos
    RIVER_COLOR = (54, 120, 190)

    env_tiles = spr_manager(r"data/sprites/tiles_sheet.png")

    def __init__(self, seed):
        self.seed = seed
        # Ruido independiente del de altura (offset de seed), para que
        # los ríos no queden pegados a la forma del terreno.
        self.river_noise = noise2(seed + 1)
        self._site_cache = {}

        # Carga del spritesheet y armado de biomas ACÁ ADENTRO a propósito:
        # esto corre cuando creás map_gen(...), no cuando se hace el import
        # del módulo. Asegurate de crear tu map_gen(...) DESPUÉS de
        # pygame.display.set_mode(...) en tu main, o vas a seguir viendo
        # el mismo error de conversión.
        self.biomes = [
            {"name": "pradera",     "tint": (0, 0, 0),       "spr": self.env_tiles.get_sprite(0, 0, 32, 32)},
            {"name": "bosque",      "tint": (-30, -10, -25), "spr": self.env_tiles.get_sprite(32, 0, 32, 32)},
            {"name": "sabana",      "tint": (35, 15, -45),   "spr": self.env_tiles.get_sprite(0, 0, 32, 32)},
            {"name": "tundra",      "tint": (-25, -5, 15),   "spr": self.env_tiles.get_sprite(32*3, 0, 32, 32)},
            {"name": "jungla",      "tint": (35, 15, -45),   "spr": self.env_tiles.get_sprite(32*3, 0, 32, 32)},
        ]

    def _hash_cell(self, ccx, ccy):
        n = (ccx * 374761393) ^ (ccy * 668265263) ^ (self.seed * 2147483647)
        n = (n ^ (n >> 13)) * 1274126177
        return (n ^ (n >> 16)) & 0xffffffff

    def _site(self, ccx, ccy):
        """Punto Voronoi (con jitter) y bioma asignado a una celda de la grilla."""
        key = (ccx, ccy)
        cached = self._site_cache.get(key)
        if cached is not None:
            return cached
        rng = random.Random(self._hash_cell(ccx, ccy))
        site_x = (ccx + rng.random()) * self.VORONOI_CELL_SIZE
        site_y = (ccy + rng.random()) * self.VORONOI_CELL_SIZE
        biome = self.biomes[rng.randrange(len(self.biomes))]
        self._site_cache[key] = (site_x, site_y, biome)
        return site_x, site_y, biome

    def get_biome(self, world_tx, world_ty):
        """Bioma del punto Voronoi más cercano (busca en las 9 celdas vecinas)."""
        ccx = math.floor(world_tx / self.VORONOI_CELL_SIZE)
        ccy = math.floor(world_ty / self.VORONOI_CELL_SIZE)
        best_biome, best_dist = None, None
        for oy in (-1, 0, 1):
            for ox in (-1, 0, 1):
                sx, sy, biome = self._site(ccx + ox, ccy + oy)
                d = (world_tx - sx) ** 2 + (world_ty - sy) ** 2
                if best_dist is None or d < best_dist:
                    best_dist, best_biome = d, biome
        return best_biome

    def is_river(self, world_tx, world_ty):
        """Truco de 'ridge noise': donde el ruido cruza ~0.5 se forma una línea sinuosa."""
        n = self.river_noise.fbm(world_tx * self.RIVER_FREQUENCY,
                                  world_ty * self.RIVER_FREQUENCY)
        return abs(n - 0.5) < self.RIVER_WIDTH

    def overlay(self, height, world_tx, world_ty):
        """
        Devuelve (biome, color, walkable) si hay que sobrescribir el
        tile base (por estar en la franja de biomas), o None si el
        tile se queda con su terreno normal (agua, arena, nieve, etc.
        quedan intactos porque están fuera del rango).
        """
        if not (self.BIOME_MIN_HEIGHT < height <= self.BIOME_MAX_HEIGHT):
            return None

        if self.is_river(world_tx, world_ty):
            return "rio", self.RIVER_COLOR, False

        _, base_color, base_walkable = height_map(height)
        biome = self.get_biome(world_tx, world_ty)
        r, g, b = base_color
        tr, tg, tb = biome["tint"]
        color = (
            max(0, min(255, r + tr)),
            max(0, min(255, g + tg)),
            max(0, min(255, b + tb)),
        )
        return biome["name"], color, base_walkable, biome["spr"]


class tile:
    __slots__ = ("height", "biome", "color", "walkable", "spr")

    def __init__(self, height, overlay=None):
        name, color, walkable = height_map(height)
        spr = None  # terreno base (agua, arena, montania, nieve) todavía sin sprite propio
        if overlay is not None:
            name, color, walkable, spr = overlay
        self.height = height
        self.biome = name
        self.color = color
        self.walkable = walkable
        self.spr = spr


class chunk:
    def __init__(self, cx, cy, size, noise_gen: noise2, features: map_features):
        self.cx = cx
        self.cy = cy
        self.size = size
        self.instances = []  # bloques/objetos colocados en este chunk (ver add_instance)
        self.entities = []   # entidades registradas en este chunk (ver add_entity)
        self.tiles = self._generate(noise_gen, features)
        self.surface = self._build_surface()  # placeholder visual, ver nota al final
 
    def _generate(self, noise_gen, features):
        tiles = [[None] * self.size for _ in range(self.size)]
        base_x = self.cx * self.size
        base_y = self.cy * self.size
        for ty in range(self.size):
            for tx in range(self.size):
                world_tx = base_x + tx
                world_ty = base_y + ty
                h = noise_gen.fbm(world_tx, world_ty)
                overlay = features.overlay(h, world_tx, world_ty)
                tiles[ty][tx] = tile(h, overlay)
        return tiles
 
    def _build_surface(self):
        px = self.size * tile_size
        surf = pygame.Surface((px, px))
        for ty in range(self.size):
            for tx in range(self.size):
                t = self.tiles[ty][tx]
                rect = pygame.Rect(tx * tile_size, ty * tile_size, tile_size, tile_size)
                if t.spr is not None:
                    surf.blit(t.spr, rect)
                else:
                    surf.fill(t.color, rect)
        return surf
 
    @property
    def world_pos(self):
        """Esquina superior izquierda del chunk, en píxeles del mundo"""
        return pygame.Vector2(self.cx * self.size * tile_size, self.cy * self.size * tile_size)
 
    def get_tile(self, local_x, local_y):
        if 0 <= local_x < self.size and 0 <= local_y < self.size:
            return self.tiles[local_y][local_x]
        return None


class map_gen:
    """
    Mundo procedural infinito basado en chunks.
 
    - self.chunks guarda en memoria TODOS los chunks que se han generado
      alguna vez (dict, nunca se borra por defecto), incluidos los que
      quedaron fuera del alcance del jugador. Así, si vuelve a esa zona,
      no se regenera el terreno, solo se reactiva.
    - self.active_chunks es el subconjunto que rodea al jugador ahora
      mismo (radio configurable) y es lo único que se procesa/dibuja.
    """
 
    def __init__(self, seed=None, chunk_size=16, render_radius=2):
        self.seed = seed if seed is not None else random.randint(0, 999_999)
        self.noise_gen = noise2(self.seed)
        self.features = map_features(self.seed)
        self.chunk_size = chunk_size
        self.render_radius = render_radius  # radio de chunks alrededor del jugador
 
        self.chunks = {}            # (cx, cy) -> Chunk  (almacenamiento permanente)
        self.active_chunks = set()  # (cx, cy) actualmente cerca del jugador
        self.player_chunk = None
 
    # --------------------------------------------------------
    def world_to_chunk(self, world_x, world_y):
        """Coordenadas de píxel del mundo -> coordenadas de chunk (soporta negativos)"""
        chunk_px = self.chunk_size * tile_size
        cx = math.floor(world_x / chunk_px)
        cy = math.floor(world_y / chunk_px)
        return cx, cy
 
    def get_or_generate_chunk(self, cx, cy):
        key = (cx, cy)
        _chunk = self.chunks.get(key)
        if _chunk is None:
            _chunk = chunk(cx, cy, self.chunk_size, self.noise_gen, self.features)
            self.chunks[key] = _chunk
        return _chunk
 
    # --------------------------------------------------------
    def update(self, player):
        """
        Llamar una vez por frame. Detecta el chunk del jugador, genera
        (o recupera de memoria) los chunks en el radio configurado y
        actualiza el set de chunks activos. El resto de chunks sigue
        en self.chunks pero no se procesa ni se dibuja.
        """
        cx, cy = self.world_to_chunk(player.position.x, player.position.y)
 
        if (cx, cy) == self.player_chunk:
            return  # el jugador sigue en el mismo chunk, nada que hacer
 
        self.player_chunk = (cx, cy)
        new_active = set()
 
        for oy in range(-self.render_radius, self.render_radius + 1):
            for ox in range(-self.render_radius, self.render_radius + 1):
                ccx, ccy = cx + ox, cy + oy
                self.get_or_generate_chunk(ccx, ccy)
                new_active.add((ccx, ccy))
 
        self.active_chunks = new_active
 
    # --------------------------------------------------------
    def draw(self, camera, screen):
        """Dibuja solo los chunks activos que además sean visibles por la cámara"""
        chunk_px = self.chunk_size * tile_size
        cam_rect = camera.camera
 
        for key in self.active_chunks:
            chunk = self.chunks.get(key)
            if chunk is None:
                continue
 
            chunk_rect = pygame.Rect(chunk.world_pos.x, chunk.world_pos.y, chunk_px, chunk_px)
            if not cam_rect.colliderect(chunk_rect):
                continue  # activo pero fuera de cámara, no se dibuja
 
            screen.blit(chunk.surface, camera.apply_rect(chunk_rect))
 
    # --------------------------------------------------------
    def get_tile_at_world(self, world_x, world_y):
        """Tile correspondiente a una posición del mundo en píxeles (genera el chunk si hace falta)"""
        chunk_px = self.chunk_size * tile_size
        cx, cy = self.world_to_chunk(world_x, world_y)
        chunk = self.get_or_generate_chunk(cx, cy)
 
        local_x = int((world_x - cx * chunk_px) / tile_size)
        local_y = int((world_y - cy * chunk_px) / tile_size)
        return chunk.get_tile(local_x, local_y)
 
    def is_walkable(self, world_x, world_y):
        tile = self.get_tile_at_world(world_x, world_y)
        return tile.walkable if tile else False
 
    # --------------------------------------------------------
    def unload_far_chunks(self, max_distance):
        """
        OPCIONAL, no se llama por defecto. Si algún día el uso de RAM
        se vuelve un problema en sesiones muy largas, esto elimina de
        verdad los chunks a más de max_distance chunks del jugador.
        Por defecto todo se conserva en memoria, tal como se pidió.
        """
        if self.player_chunk is None:
            return
        cx, cy = self.player_chunk
        to_remove = [
            key for key in self.chunks
            if max(abs(key[0] - cx), abs(key[1] - cy)) > max_distance
        ]
        for key in to_remove:
            del self.chunks[key]

    def add_instance(self, instance_data, world_x, world_y):
        """
        Registra un "bloque"/objeto colocado en el mundo (fuera del
        terreno base generado por ruido) en el chunk que le corresponde,
        para que quede incluido al guardar. instance_data debe ser un
        dict serializable en JSON, ej: {"tipo": "cofre", "x": .., "y": ..}
        WIP: falta definir el esquema definitivo de instancias.
        """
        cx, cy = self.world_to_chunk(world_x, world_y)
        chunk = self.get_or_generate_chunk(cx, cy)
        chunk.instances.append(instance_data)
 
    def add_entity(self, entity):
        """
        Registra una entidad en el chunk que le corresponde según su
        posición actual, para que se incluya al guardar el mundo.
        Usa entity.to_dict() si el objeto lo define; si no, arma un
        dict básico con los atributos más comunes.
        WIP: cada tipo de entidad debería terminar definiendo su propio
        to_dict()/from_dict() para guardarse y reconstruirse bien.
        """
        if hasattr(entity, "to_dict"):
            data = entity.to_dict()
        else:
            data = {
                "tipo": type(entity).__name__,
                "x": entity.position.x,
                "y": entity.position.y,
                "hp": getattr(entity, "hp", None),
            }
 
        cx, cy = self.world_to_chunk(entity.position.x, entity.position.y)
        chunk = self.get_or_generate_chunk(cx, cy)
        chunk.entities.append(data)
 
    def save(self, filepath):
        """
        Guarda en un .json TODOS los chunks actualmente en memoria
        (self.chunks) -- no solo los activos -- junto con el terreno
        (alturas de cada tile), las instancias (bloques) y las
        entidades registradas en cada uno.
        WIP: el esquema puede cambiar más adelante (sprites, inventario,
        IA de entidades, etc.). instance_data/entity data deben ser
        siempre serializables en JSON (nada de Surface, Rect, etc).
        """
        data = {
            "seed": self.seed,
            "chunk_size": self.chunk_size,
            "render_radius": self.render_radius,
            "chunks": [],
        }
 
        for (cx, cy), chunk in self.chunks.items():
            data["chunks"].append({
                "cx": cx,
                "cy": cy,
                "tiles": [[tile.height for tile in row] for row in chunk.tiles],
                "instances": chunk.instances,
                "entities": chunk.entities,
            })
 
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f)
 
    def load(self, filepath):
        """
        Carga un mundo previamente guardado con save(). Reconstruye
        self.chunks a partir de las alturas guardadas (no las vuelve a
        generar con ruido, por si en el futuro el terreno se edita) y
        restaura instancias/entidades por chunk.
        WIP: no reconstruye entidades reales (jugador, enemigos, etc.),
        deja los dicts crudos en chunk.entities para que el código que
        las maneje decida cómo instanciarlas de nuevo.
        """
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
 
        self.seed = data["seed"]
        self.noise_gen = noise2(self.seed)
        self.features = map_features(self.seed)
        self.chunk_size = data["chunk_size"]
        self.render_radius = data["render_radius"]
        self.chunks = {}
        self.active_chunks = set()
        self.player_chunk = None
 
        for chunk_data in data["chunks"]:
            cx, cy = chunk_data["cx"], chunk_data["cy"]
            self.chunks[(cx, cy)] = chunk.from_data(
                cx, cy, self.chunk_size,
                chunk_data["tiles"],
                chunk_data.get("instances", []),
                chunk_data.get("entities", []),
            )