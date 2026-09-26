import pygame, random, math, json

from data.modules.states.noise2 import noise2
from data.modules.services.spr_manager import spr_manager
from data.modules.type.types.blocks import load_blocks 
from data.modules.type.types.entities import player


tile_size = 32


class map_features:
    """
    Genera biomas (celdas tipo Voronoi/Worley) y ríos de forma
    DETERMINISTA a partir de la seed del mundo y la posición en
    tiles. No guarda estado que dependa del orden de generación de
    chunks: la celda Voronoi, la variante de sprite de cada tile y el
    ruido de río de una posición dan siempre el mismo resultado, la
    calcules cuando la calcules, así que no hace falta persistir nada
    de esto en el save().

    IMPORTANTE sobre el rango de alturas: en self.terrain_range, "pasto"
    es 0.42 < h <= 0.62, y 0.62 es donde EMPIEZA "montania". Dejé
    BIOME_MIN_HEIGHT/BIOME_MAX_HEIGHT en (0.42, 0.62) para que caiga
    dentro de pasto. Si en realidad querías la franja de montaña
    (todo lo que es > 0.62), cambia estos dos valores a (0.62, 0.83).

    PROPS (plantas/árboles/minerales, TALABLES/MINABLES): en vez de
    tirar un dado por cada tile -lo que puede amontonar props pegados
    unos a otros-, se usa el MISMO truco que los sitios Voronoi de
    bioma: el mundo se divide en una grilla de celdas de
    PROP_CELL_SIZE x PROP_CELL_SIZE tiles, y cada celda aporta COMO
    MÁXIMO un punto candidato (con jitter determinista, acotado al
    centro de la celda por PROP_JITTER_MARGIN). Solo ESE tile puntual
    puede terminar con un prop, y la distancia entre dos candidatos de
    celdas vecinas queda GARANTIZADA en al menos 2*PROP_JITTER_MARGIN
    + 1 tiles.

    Cada entrada de "props" (tanto en un bioma como en self.terrain_range)
    es una tupla (clase, sprite, chance): la clase es una subclase de
    world_prop (tree/bush/mineral, ver data/modules/type/world_prop.py)
    que se instancia recién en chunk._generate() -no acá, donde solo
    se define QUÉ puede salir y con qué probabilidad relativa-. El
    tamaño en pantalla y el hitbox salen del sprite real, nunca de un
    número aparte.
    """

    BIOME_MIN_HEIGHT = 0.42
    BIOME_MAX_HEIGHT = 0.62

    VORONOI_CELL_SIZE = 96     # tamaño de celda en tiles; súbelo para biomas más grandes
    RIVER_FREQUENCY = 0.01     # más bajo = ríos más largos y suaves
    RIVER_WIDTH = 0.015        # más alto = ríos más anchos
    RIVER_COLOR = (54, 120, 190)

    PROP_CELL_SIZE = 6         # tamaño de celda de props, en tiles
    PROP_JITTER_MARGIN = 2     # margen desde el borde de la celda (ver _prop_site)

    def __init__(self, seed):
        self.seed = seed

        blocks = load_blocks()

        self.river_noise = noise2(seed + 1)
        self._site_cache = {}
        self._prop_site_cache = {}

        self.env_tiles = spr_manager(r"data/sprites/tile_sheet.png")

        self.biomes = [
            {
                "name": "pradera",
                "tint": (0, 0, 0),
                "variants": [
                    (self.env_tiles.get_sprite(0, 0, 32, 32), 50),
                    (self.env_tiles.get_sprite(32*2, 0, 32, 32), 20),
                    (self.env_tiles.get_sprite(32, 0, 32, 32), 10),
                    (self.env_tiles.get_sprite(32*3, 0, 32, 32), 15),
                    (self.env_tiles.get_sprite(32*5, 0, 32, 32), 5),
                ],
                "props": [
                    (blocks.get("sunflower"), 0.1),
                    (blocks.get("fungus"), 0.07),
                    (blocks.get("oak-tree-1"), 0.1),
                    (blocks.get("oak-tree-2"), 0.08),
                    (blocks.get("stone-chunk"), 0.1),
                    (blocks.get("copper-chunk"), 0.07),
                    (blocks.get("coal-chunk"), 0.07),
                ],
            },
            {
                "name": "bosque",
                "tint": (-30, -10, -25),
                "variants": [
                    (self.env_tiles.get_sprite(0, 0, 32, 32), 80),
                    (self.env_tiles.get_sprite(32*2, 0, 32, 32), 20),
                ],
                "props": [
                    (blocks.get("sunflower"), 0.1),
                    (blocks.get("oak-tree-1"), 0.2),
                    (blocks.get("oak-tree-2"), 0.1),
                    (blocks.get("stone-chunk"), 0.09),
                    (blocks.get("copper-chunk"), 0.05),
                    (blocks.get("coal-chunk"), 0.05),
                ],
            },
            {
                "name": "sabana",
                "tint": (35, 15, -45),
                "variants": [
                    (self.env_tiles.get_sprite(32*5, 0, 32, 32), 40),
                    (self.env_tiles.get_sprite(32*7, 0, 32, 32), 35),
                    (self.env_tiles.get_sprite(32*6, 0, 32, 32), 25)
                ],
                "props": [
                    (blocks.get("oak-tree-1"), 0.09),
                    (blocks.get("oak-tree-2"), 0.06),
                    (blocks.get("stone-chunk"), 0.07),
                    (blocks.get("copper-chunk"), 0.04),
                    (blocks.get("coal-chunk"), 0.04),
                ],
            },
            {
                "name": "tundra",
                "tint": (-25, -5, 15),
                "variants": [
                    (self.env_tiles.get_sprite(32*12, 0, 32, 32), 50),
                    (self.env_tiles.get_sprite(32*13, 0, 32, 32), 30),
                    (self.env_tiles.get_sprite(32*14, 0, 32, 32), 20),
                ],
                "props": [
                    (blocks.get("sunflower"), 0.2),
                    (blocks.get("oak-tree-1"), 0.5),
                    (blocks.get("oak-tree-2"), 0.05),
                    (blocks.get("stone-chunk"), 0.05),
                    (blocks.get("copper-chunk"), 0.03),
                    (blocks.get("coal-chunk"), 0.03),
                ],
            },
            {
                "name": "jungla",
                "tint": (35, 15, -45),
                "variants": [
                    (self.env_tiles.get_sprite(32*11, 0, 32, 32), 40),
                    (self.env_tiles.get_sprite(32*10, 0, 32, 32), 20),
                    (self.env_tiles.get_sprite(32*9, 0, 32, 32), 30),
                    (self.env_tiles.get_sprite(32*8, 0, 32, 32), 10),
                ],
                "props": [
                    (blocks.get("sunflower"), 0.2),
                    (blocks.get("oak-tree-1"), 0.1),
                    (blocks.get("oak-tree-2"), 0.09),
                    (blocks.get("stone-chunk"), 0.02),
                    (blocks.get("copper-chunk"), 0.009),
                    (blocks.get("coal-chunk"), 0.009),
                ],
            },
            {
                "name": "magic_forest",
                "tint": (45, 25, -55),
                "variants": [
                    (self.env_tiles.get_sprite(32*17, 0, 32, 32), 40),
                    (self.env_tiles.get_sprite(32*18, 0, 32, 32), 30),
                    (self.env_tiles.get_sprite(32*19, 0, 32, 32), 30),
                ],
                "props": [
                    (blocks.get("sunflower"), 0.1),
                    (blocks.get("fungus"), 0.2),
                    (blocks.get("stone-chunk"), 0.02),
                ],
            },
        ]

        self.terrain_range = [
            {
                "max_h": 0.2, "name": "agua_profunda", "color": (17, 63, 122), "walkable": False,
                "variants": [
                    (self.env_tiles.get_sprite(32*4, 32, 32, 32), 100),
                ],
            },
            {
                "max_h": 0.33, "name": "agua", "color": (31, 99, 173), "walkable": False,
                "variants": [
                    (self.env_tiles.get_sprite(32*3, 32, 32, 32), 100),
                ],
            },
            {
                "max_h": 0.38, "name": "arena", "color": (231, 213, 158), "walkable": True,
                "variants": [
                    (self.env_tiles.get_sprite(0, 32, 32, 32), 85),
                    (self.env_tiles.get_sprite(32*2, 32, 32, 32), 15),
                ],
            },
            {
                "max_h": 0.68, "name": "pasto", "color": (85, 158, 68), "walkable": True,
                "variants": [
                    (self.env_tiles.get_sprite(0, 0, 32, 32), 100),
                ]
            },
            {
                "max_h": 0.87, "name": "montania", "color": (120, 114, 108), "walkable": True,
                "variants": [
                    (self.env_tiles.get_sprite(32*5, 0, 32, 32), 100),
                ],
                "props": [
                    (blocks.get("stone-chunk"), 0.04),
                ],
            },
            {
                "max_h": 0.9, "name": "nieve", "color": (240, 240, 245), "walkable": True,
                "variants": [
                    (self.env_tiles.get_sprite(32*15, 0, 32, 32), 60),
                    (self.env_tiles.get_sprite(32*16, 0, 32, 32), 40),
                ],
            },
        ]

    def _hash_cell(self, ccx, ccy):
        n = (ccx * 374761393) ^ (ccy * 668265263) ^ (self.seed * 2147483647)
        n = (n ^ (n >> 13)) * 1274126177
        return (n ^ (n >> 16)) & 0xffffffff

    def _hash_variant(self, world_tx, world_ty, salt=0):
        """
        Hash independiente del de los sitios Voronoi (constante y offset
        de seed distintos), para que la variante elegida no quede
        correlacionada con el bioma elegido. "salt" separa el roll de
        biomas del roll de terreno base, para que no coincidan en la
        misma posición. Devuelve un float determinista en [0, 1) a
        partir de (seed, world_tx, world_ty, salt).
        """
        n = (world_tx * 2654435761) ^ (world_ty * 40503) ^ ((self.seed + 1 + salt) * 2246822519)
        n = (n ^ (n >> 13)) * 3266489917
        n = n ^ (n >> 16)
        return (n & 0xffffffff) / 0xffffffff

    def _pick_variant(self, entry, world_tx, world_ty, salt=0):
        """
        Elige, de forma determinista según la posición del tile, cuál
        sprite de entry["variants"] le toca a ESTE tile (bioma o
        terreno base), respetando los pesos de probabilidad.
        """
        variants = entry.get("variants")
        if not variants:
            return None
        if len(variants) == 1:
            return variants[0][0]

        total = sum(weight for _, weight in variants)
        if total <= 0:
            return variants[0][0]

        roll = self._hash_variant(world_tx, world_ty, salt) * total
        acc = 0.0
        for spr, weight in variants:
            acc += weight
            if roll <= acc:
                return spr
        return variants[-1][0]  # fallback por redondeo de floats

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

    def _terrain_for_height(self, height):
        """Entrada de self.terrain_range (dict) que corresponde a esta altura."""
        for entry in self.terrain_range:
            if height <= entry["max_h"]:
                return entry
        return self.terrain_range[-1]

    def base_terrain(self, height, world_tx, world_ty):
        """
        Terreno base (agua, arena, pasto, montania, nieve...) para un
        tile FUERA de la franja de biomas, con su propia variante de
        sprite ya resuelta -mismo criterio determinista que overlay()-.
        Devuelve (name, color, walkable, spr).
        """
        terrain = self._terrain_for_height(height)
        spr = self._pick_variant(terrain, world_tx, world_ty, salt=2)
        return terrain["name"], terrain["color"], terrain["walkable"], spr

    def overlay(self, height, world_tx, world_ty, biome=None, river=None):
        """
        Devuelve (biome, color, walkable, spr) si hay que sobrescribir el
        tile base (por estar en la franja de biomas), o None si el
        tile se queda con su terreno normal (agua, arena, nieve, etc.
        quedan intactos porque están fuera del rango). "spr" ya viene
        resuelto a la variante concreta que le toca a ESTE tile.

        "biome"/"river" se pueden pasar ya calculados -tile_data() lo
        hace para no llamar a get_biome()/is_river() dos veces por
        tile-; si se dejan en None, este método los resuelve solo.
        """
        if not (self.BIOME_MIN_HEIGHT < height <= self.BIOME_MAX_HEIGHT):
            return None

        if river is None:
            river = self.is_river(world_tx, world_ty)
        if river:
            return "rio", self.RIVER_COLOR, False, None

        if biome is None:
            biome = self.get_biome(world_tx, world_ty)

        base = self._terrain_for_height(height)
        r, g, b = base["color"]
        tr, tg, tb = biome["tint"]
        color = (
            max(0, min(255, r + tr)),
            max(0, min(255, g + tg)),
            max(0, min(255, b + tb)),
        )
        spr = self._pick_variant(biome, world_tx, world_ty, salt=1)
        return biome["name"], color, base["walkable"], spr

    def tile_data(self, height, world_tx, world_ty):
        """
        Punto de entrada único para chunk._generate(): resuelve terreno
        (bioma -con su variante y tint- o terreno base, según
        corresponda) Y decide si a este tile le toca un prop, todo en
        un solo paso -is_river()/get_biome() se calculan COMO MUCHO
        una vez por tile, no dos-.

        Devuelve (tile_result, prop):
          - tile_result: (name, color, walkable, spr)
          - prop: (clase, sprite) o None -la clase es una subclase de
            world_prop (tree/bush/mineral); la instancia recién se
            crea en chunk._generate(), con la posición ya resuelta-
        """
        in_biome_range = self.BIOME_MIN_HEIGHT < height <= self.BIOME_MAX_HEIGHT
        river = self.is_river(world_tx, world_ty) if in_biome_range else False
        biome = self.get_biome(world_tx, world_ty) if (in_biome_range and not river) else None

        tile_result = self.overlay(height, world_tx, world_ty, biome=biome, river=river)
        if tile_result is None:
            tile_result = self.base_terrain(height, world_tx, world_ty)

        prop = self.pick_prop(height, world_tx, world_ty, biome=biome, river=river)
        return tile_result, prop

    def _hash_prop_cell(self, pcx, pcy):
        n = (pcx * 668265263) ^ (pcy * 374761393) ^ ((self.seed + 7) * 2654435761)
        n = (n ^ (n >> 13)) * 2246822519
        return (n ^ (n >> 16)) & 0xffffffff

    def _prop_site(self, pcx, pcy):
        """
        Punto candidato a prop dentro de la celda (pcx, pcy) de
        PROP_CELL_SIZE x PROP_CELL_SIZE tiles, con jitter determinista
        -mismo criterio que _site() para los sitios Voronoi de bioma,
        pero con el jitter acotado al centro de la celda vía
        PROP_JITTER_MARGIN-. Sin ese margen, dos celdas vecinas podrían
        elegir candidatos pegados al borde compartido y terminar casi
        superpuestos. Con el margen, la distancia mínima GARANTIZADA
        entre candidatos de celdas vecinas es 2*PROP_JITTER_MARGIN + 1
        tiles (en vez de depender solo de la suerte del jitter).

        Devuelve (tile_x, tile_y, roll): la celda entera comparte un
        único "roll" (float determinista en [0, 1)) que decide CUÁL
        prop del bioma/terreno le toca a su candidato, si le toca alguno.
        """
        key = (pcx, pcy)
        cached = self._prop_site_cache.get(key)
        if cached is not None:
            return cached
        rng = random.Random(self._hash_prop_cell(pcx, pcy))
        m = self.PROP_JITTER_MARGIN
        jitter_x = rng.randrange(m, self.PROP_CELL_SIZE - m)
        jitter_y = rng.randrange(m, self.PROP_CELL_SIZE - m)
        tile_x = pcx * self.PROP_CELL_SIZE + jitter_x
        tile_y = pcy * self.PROP_CELL_SIZE + jitter_y
        roll = rng.random()
        result = (tile_x, tile_y, roll)
        self._prop_site_cache[key] = result
        return result

    def pick_prop(self, height, world_tx, world_ty, biome=None, river=None):
        """
        Devuelve (clase, sprite) si a ESTE tile le toca ser el ÚNICO
        prop de su celda de PROP_CELL_SIZE tiles, o None en cualquier
        otro caso. Funciona tanto para props de bioma (pasto/bosque/
        etc, dentro de la franja de biomas) como para props de terreno
        base (ej. nodos de mineral en montania, fuera de la franja de
        biomas) -en ambos casos busca la lista "props" de la entrada
        que corresponda (biome o self.terrain_range) con el mismo
        formato (clase, sprite, chance)-.

        Chequea primero si el tile es el candidato de su celda -barato,
        no toca is_river()/get_biome()- antes de resolver el resto:
        para la enorme mayoría de tiles (los que no son candidatos de
        ninguna celda) esto no cuesta casi nada.

        "biome"/"river" se pueden pasar ya calculados (ver tile_data);
        si se dejan en None, se resuelven acá -pero solo si hace
        falta, es decir, solo para el candidato de la celda-.
        """
        pcx = math.floor(world_tx / self.PROP_CELL_SIZE)
        pcy = math.floor(world_ty / self.PROP_CELL_SIZE)
        tile_x, tile_y, roll = self._prop_site(pcx, pcy)
        if (world_tx, world_ty) != (tile_x, tile_y):
            return None  # este tile no es el candidato de su celda

        in_biome_range = self.BIOME_MIN_HEIGHT < height <= self.BIOME_MAX_HEIGHT

        if in_biome_range:
            if river is None:
                river = self.is_river(world_tx, world_ty)
            if river:
                return None
            if biome is None:
                biome = self.get_biome(world_tx, world_ty)
            entry = biome
        else:
            # Fuera de la franja de biomas: props de terreno base
            # (ej. minerales en montania).
            entry = self._terrain_for_height(height)

        props = entry.get("props")
        if not props:
            return None

        acc = 0.0
        for prop_cls, chance in props:
            acc += chance
            if roll < acc:
                return prop_cls
        return None


class tile:
    __slots__ = ("height", "biome", "color", "walkable", "spr")

    def __init__(self, height, data):
        name, color, walkable, spr = data
        self.height = height
        self.biome = name
        self.color = color
        self.walkable = walkable
        self.spr = spr


class chunk:
    def __init__(self, cx, cy, size, noise_gen: noise2, features: map_features, destroyed_props=None):
        self.cx = cx
        self.cy = cy
        self.size = size
        self.instances = []  # bloques/objetos colocados en este chunk (ver add_instance)
        self.entities = []   # entidades registradas en este chunk (ver add_entity)

        self.destroyed_props = destroyed_props if destroyed_props is not None else set()

        self.props = []

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
                data, prop = features.tile_data(h, world_tx, world_ty)
                tiles[ty][tx] = tile(h, data)

                if prop is not None and (world_tx, world_ty) not in self.destroyed_props:
                    # OJO: "prop" es la MISMA instancia que devuelve
                    # load_blocks() (blocks.get("oak-tree-1"), etc.),
                    # compartida por TODO el mundo -no una clase-.
                    # Si se usa tal cual, todos los tiles que sortean
                    # "oak-tree-1" terminan apuntando al mismo objeto
                    # y set_pos() mueve ese único árbol de un lado a
                    # otro en vez de crear uno en cada sitio. Por eso
                    # hay que clonarlo antes de reposicionarlo.
                    prop_template = prop

                    # El tamaño real (para centrar en x y apoyar la
                    # base en el borde inferior del tile) sale del
                    # sprite, nunca de un número aparte -antes acá se
                    # usaba un "size_px" (1/2/3) que NO coincidía con
                    # el tamaño real del sprite (32/64/128px) y
                    # descentraba bastante los props grandes-.
                    real_w = prop_template.spr.get_width()
                    real_h = prop_template.spr.get_height()
                    world_px = world_tx * tile_size + tile_size // 2 - real_w // 2
                    world_py = world_ty * tile_size + tile_size - real_h

                    instance = prop_template.clone()
                    instance.set_pos(world_px, world_py)
                    instance.grid_pos = (world_tx, world_ty)
                    self.props.append(instance)
        return tiles

    def mark_prop_destroyed(self, prop):
        """
        Marca un prop como destruido de forma persistente PARA ESTE
        CHUNK: lo saca de self.props y recuerda su celda en
        self.destroyed_props, para que si el chunk se regenera desde
        cero no vuelva a aparecer. Con el comportamiento por defecto de
        map_gen (los chunks quedan en memoria para siempre y
        unload_far_chunks() no se llama solo) esto alcanza para que un
        árbol talado no reaparezca durante la partida.
        """
        if prop in self.props:
            self.props.remove(prop)
        if getattr(prop, "grid_pos", None) is not None:
            self.destroyed_props.add(prop.grid_pos)

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
    def draw(self, camera, screen, pls):
        """
        Dibuja los chunks activos visibles por la cámara y, encima, sus
        props en 3 CAPAS FIJAS de profundidad (no un Y-sort global):

            1. props "ground"  (bush, mineral, ...)  -por detrás/abajo-
            2. pls             (jugador, npc, ...)   -en el medio-
            3. props "canopy"  (tree, ...)           -por delante/arriba-

        Así el jugador siempre camina "sobre" arbustos/minerales y
        siempre "por debajo" de la copa de los árboles, sin importar la
        posición y real de cada uno -da más sensación de profundidad
        que ordenar todo junto por world_y, a costa de que dos props de
        capas distintas nunca se tapen "bien" entre sí (no hace falta:
        conceptualmente uno es piso y el otro es techo)-. Dentro de
        cada capa de props sí se sigue ordenando por world_y, para que
        no haya parpadeos raros si dos props del mismo tipo se
        superponen.

        Args:
            pls: iterable de entidades con .rect y .draw(camera, screen)
                -por ejemplo [self.plr, self.npc]- que se dibujan en la
                capa del medio. Reemplaza a llamar a entity.draw() por
                separado después de world.draw(): ahora hay que pasarlas
                acá para que los árboles puedan quedar por encima.

        LIMITACIÓN CONOCIDA: un prop se guarda en el chunk que
        contiene el tile donde nace, y solo se dibuja si ESE chunk
        está activo. Un árbol grande (128px) cerca del borde puede
        desaparecer un frame antes de lo esperado si su chunk se
        desactiva mientras la copa todavía sería visible. Para
        mundos con render_radius chico esto casi no se nota; si
        molesta, aumentá render_radius en vez de tocar esto.
        """
        chunk_px = self.chunk_size * tile_size
        cam_rect = camera.camera

        ground_props = []
        canopy_props = []

        for key in self.active_chunks:
            _chunk = self.chunks.get(key)
            if _chunk is None:
                continue

            chunk_rect = pygame.Rect(_chunk.world_pos.x, _chunk.world_pos.y, chunk_px, chunk_px)
            if not cam_rect.colliderect(chunk_rect):
                continue  # activo pero fuera de cámara, no se dibuja

            screen.blit(_chunk.surface, camera.apply_rect(chunk_rect))

            for prop in _chunk.props:
                if not prop.active or not cam_rect.colliderect(prop.rect):
                    continue
                if prop.draw_layer == "canopy":
                    canopy_props.append(prop)
                else:
                    ground_props.append(prop)

        ground_props.sort(key=lambda p: p.world_y)
        canopy_props.sort(key=lambda p: p.world_y)

        for prop in ground_props:
            prop.draw(camera, screen)

        for entity in pls:
            entity.draw(camera, screen)
            if entity is player:
                print("Detecta jugador")
                entity.inventory.draw(screen)

        for prop in canopy_props:
            prop.draw(camera, screen)

        for entity in pls:
            if isinstance(entity, player):
                entity.inventory.draw(camera, screen)

    def get_tile_at_world(self, world_x, world_y):
        """Tile correspondiente a una posición del mundo en píxeles (genera el chunk si hace falta)"""
        chunk_px = self.chunk_size * tile_size
        cx, cy = self.world_to_chunk(world_x, world_y)
        _chunk = self.get_or_generate_chunk(cx, cy)

        local_x = int((world_x - cx * chunk_px) / tile_size)
        local_y = int((world_y - cy * chunk_px) / tile_size)
        return _chunk.get_tile(local_x, local_y)

    def is_walkable(self, world_x, world_y):
        t = self.get_tile_at_world(world_x, world_y)
        return t.walkable if t else False

    def is_walkable_tile(self, tile_x, tile_y):
        """
        Igual que is_walkable(), pero recibe coordenadas de TILE en vez
        de píxeles -pensado para pasarlo directo como callback a
        Entity.random_patrol()/Entity.find_path(), que trabajan en
        tiles-. Ej: entidad.random_patrol(world.is_walkable_tile, ...).
        """
        return self.is_walkable(tile_x * tile_size, tile_y * tile_size)

    def get_prop_at_world(self, world_x, world_y, radius=24):
        """
        Busca el prop interactuable ACTIVO más cercano a (world_x, world_y)
        dentro de "radius" píxeles, entre los props de los chunks
        activos. Pensado para conectar con la interacción del jugador
        (talar/minar/cosechar apuntando o hacia donde mira/está parado).

        Devuelve (chunk, prop) o (None, None) -se necesita el chunk
        para poder llamar a chunk.mark_prop_destroyed(prop) si el golpe
        lo destruye-.

        Ejemplo de uso típico (p.ej. en player.attack()):

            _chunk, prop = self.scene.world.get_prop_at_world(
                self.position.x, self.position.y, radius=40)
            if prop is not None:
                drops = prop.interact(tool="hacha", power=1)
                if drops is not None:
                    _chunk.mark_prop_destroyed(prop)
                    for item_name, amount in drops:
                        ...  # agregar al inventario
        """
        search_rect = pygame.Rect(world_x - radius, world_y - radius, radius * 2, radius * 2)
        best_chunk, best_prop, best_dist = None, None, None

        for key in self.active_chunks:
            _chunk = self.chunks.get(key)
            if _chunk is None:
                continue
            for prop in _chunk.props:
                if not prop.active or not prop.rect.colliderect(search_rect):
                    continue
                dist = (prop.rect.centerx - world_x) ** 2 + (prop.rect.centery - world_y) ** 2
                if best_dist is None or dist < best_dist:
                    best_chunk, best_prop, best_dist = _chunk, prop, dist

        return best_chunk, best_prop

    def unload_far_chunks(self, max_distance):
        """
        OPCIONAL, no se llama por defecto. Si algún día el uso de RAM
        se vuelve un problema en sesiones muy largas, esto elimina de
        verdad los chunks a más de max_distance chunks del jugador.
        Por defecto todo se conserva en memoria, tal como se pidió.

        OJO: si se llama y el jugador vuelve a esa zona, get_or_generate_chunk
        crea un chunk NUEVO (sin destroyed_props), así que los props que
        el jugador ya había talado/minado ahí reaparecerían.
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
        _chunk = self.get_or_generate_chunk(cx, cy)
        _chunk.instances.append(instance_data)

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
        _chunk = self.get_or_generate_chunk(cx, cy)
        _chunk.entities.append(data)

    def save(self, filepath):
        """
        Guarda en un .json TODOS los chunks actualmente en memoria
        (self.chunks) -- no solo los activos -- junto con el terreno
        (alturas de cada tile), las instancias (bloques) y las
        entidades registradas en cada uno.

        WIP / LIMITACIÓN CONOCIDA: todavía NO guarda destroyed_props
        (qué props se talaron/minaron), así que al cargar con load()
        todos los props de cada chunk vuelven a aparecer intactos. Si
        te importa que lo talado se mantenga entre partidas, hay que
        sumar "destroyed_props": sorted(list(_chunk.destroyed_props))
        acá y leerlo de vuelta en load().
        """
        data = {
            "seed": self.seed,
            "chunk_size": self.chunk_size,
            "render_radius": self.render_radius,
            "chunks": [],
        }

        for (cx, cy), _chunk in self.chunks.items():
            data["chunks"].append({
                "cx": cx,
                "cy": cy,
                "tiles": [[t.height for t in row] for row in _chunk.tiles],
                "instances": _chunk.instances,
                "entities": _chunk.entities,
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

        OJO: este método llama a chunk.from_data(...), que todavía NO
        existe en la clase chunk de este archivo -hace falta definirlo
        (reconstruir tiles a partir de las alturas guardadas, más
        instances/entities, y si querés que los props talados/minados
        se mantengan, también destroyed_props) antes de que load()
        funcione.
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