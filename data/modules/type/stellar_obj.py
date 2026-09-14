import pygame, math, random

from settings import G
from data.modules.states.noise2 import noise2


class stellar_obj:
    def __init__(self, x, y, r, color, mass):
        self.x = x
        self.y = y
        self.r = r
        self.color = color
        self.angle = 0
        self.mass = mass
        self.g = ((mass * G) / ((r * (1e6)) ** 2))
        self._rotation = 0.0
        self.orbit_z = 0.0     # profundidad relativa: <0 detrás, >0 delante

    def orbit(self, obj, orbit_rx, orbit_s, offset_x=0, offset_y=0, orbit_ry=None):
        self.angle += orbit_s
        if orbit_ry is None:
            orbit_ry = orbit_rx

        self.x = (obj.x + orbit_rx * math.cos(self.angle)) + offset_x
        self.y = (obj.y + orbit_ry * math.sin(self.angle)) + offset_y

        # Profundidad relativa en unidades de mundo (no normalizada -1..1).
        # tilt=0 -> órbita de frente (sin componente z, luz solo en x/y)
        # tilt=1 -> órbita de canto (ry=0): el cuerpo se desplaza en z tanto
        #           como en x, pasando realmente delante/detrás del objeto
        tilt = math.sqrt(max(0.0, 1 - (orbit_ry / orbit_rx) ** 2)) if orbit_rx else 0.0
        self.orbit_z = orbit_rx * math.sin(self.angle) * tilt

    def update(self, dt, rotation_speed=0.8):
        self._rotation += dt * rotation_speed

    def draw(self, screen, scale=1, color_rot=0, colors=None, light_source=None):
        r = self.r * scale
        cx, cy = int(self.x), int(self.y)

        light_dir = None
        if light_source is not None:
            lx = light_source.x - self.x
            ly = light_source.y - self.y
            # el sol se asume en z=0; este cuerpo está desplazado en profundidad
            # según su propia órbita (self.orbit_z, calculado en orbit())
            lz = -getattr(self, 'orbit_z', 0.0)
            dist = math.sqrt(lx*lx + ly*ly + lz*lz)
            if dist > 0:
                light_dir = (lx / dist, ly / dist, lz / dist)

        HEX_ANG = 0.225
        hexes = []

        phi = 0.0
        while phi <= math.pi:
            sin_phi = math.sin(phi)
            circumference = 2 * math.pi * sin_phi * r
            count = max(1, round(circumference / (HEX_ANG * r)))
            row_idx = round(phi / HEX_ANG)

            for i in range(count):
                theta = (2 * math.pi / count) * i
                if row_idx % 2 == 1:
                    theta += math.pi / count

                x3 = r * sin_phi * math.cos(theta)
                y3 = r * math.cos(phi)
                z3 = r * sin_phi * math.sin(theta)

                rot = self._rotation
                xr = x3 * math.cos(rot) - z3 * math.sin(rot)
                zr = x3 * math.sin(rot) + z3 * math.cos(rot)
                yr = y3

                if zr < 0:
                    continue

                sx = cx + xr
                sy = cy + yr
                cam_depth = zr / r

                height = (
                    0.5
                    + 0.25 * math.sin(phi * 3 + theta * 2)
                    + 0.15 * math.cos(phi * 5 - theta * 3 + color_rot * self._rotation)
                    + 0.10 * math.sin(phi * 7 + theta * 5)
                )
                height = max(0.0, min(1.0, height))

                if light_dir is not None:
                    # ahora incluye zr: la componente de profundidad del sol
                    # entra en juego, sobre todo cerca del tránsito
                    illum = (xr * light_dir[0] + yr * light_dir[1] + zr * light_dir[2]) / r
                    light_amt = max(0.0, illum)
                else:
                    light_amt = cam_depth

                hr = r * HEX_ANG * 0.9 * (0.75 + cam_depth * 0.25)
                hexes.append((cam_depth, sx, sy, hr, light_amt, height))

            phi += HEX_ANG

        hexes.sort(key=lambda h: h[0])

        for cam_depth, sx, sy, hr, light_amt, height in hexes:
            base_color = self._color_from_height(height, colors)
            final_color = self._apply_light(base_color, light_amt)
            border = tuple(max(0, c - 35) for c in final_color)

            pts = self._hex_points(sx, sy, hr)
            pygame.draw.polygon(screen, final_color, pts)
            pygame.draw.polygon(screen, border, pts, 1)

    # ── helpers ─────────────────────────────────────────────────────────────

    def set_pos(self, x, y):
        self.x = x
        self.y = y

    @staticmethod
    def _color_from_height(height, colors):
        if not colors:
            return (255, 255, 255)
        for threshold, color in colors:
            if height <= threshold:
                return color
        return colors[-1][1]

    @staticmethod
    def _apply_light(color, amt):
        """
        amt: 0..1 (0 = sombra, 1 = plena luz). Ambient mínimo para que el
        lado oscuro no sea negro puro.
        """
        factor = 0.12 + amt * 0.88
        return tuple(min(255, int(c * factor)) for c in color)

    @staticmethod
    def _hex_points(cx, cy, r):
        pts = []
        for i in range(6):
            a = math.radians(60 * i - 30)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        return pts


class star(stellar_obj):
    def __init__(self, x, y, r, color, mass, heat):
        super().__init__(x, y, r, color, mass)
        self.heat = heat


class planet(stellar_obj):
    def __init__(self, x, y, r, color, mass):
        super().__init__(x, y, r, color, mass)

class moon(stellar_obj):
    def __init__(self, x, y, r, color, mass):
        super().__init__(x, y, r, color, mass)


class background_stars:
    """
    Fondo estrellado en movimiento, generado UNA sola vez con noise2 y
    despues animado solo por scroll (nunca se vuelve a llamar al
    ruido en cada frame -eso si seria carisimo-).

    Como funciona la generacion (en __init__):
    - Se recorre un area "world_w x world_h" en una grilla de "cell"
      px, con un pequeño jitter aleatorio por celda (asi no queda
      perfectamente cuadriculado).
    - En cada celda se consulta noise2d(): si el valor supera
      "threshold" ahi va una estrella. Cuanto mas lo supera, mas
      grande/brillante es, y tambien "mas cerca" (se mueve un poco
      mas rapido que el resto al hacer scroll -parallax simple-),
      todo derivado del mismo valor de ruido, sin tirar mas dados.

    IMPORTANTE - el threshold asume que noise2d() devuelve algo
    aproximadamente en el rango 0..1 (como ya lo veniamos usando con
    0.97 / 0.62 en otras partes). Si al probarlo no aparece NINGUNA
    estrella, es señal de que tu noise2d en realidad devuelve otro
    rango (por ej. -1..1): probá bajar `threshold` (incluso a 0 o
    negativo) para confirmarlo, y despues subilo hasta la densidad
    que te guste.

    draw(screen, ox, oy) desplaza todo el campo por (ox, oy) -el
    mismo contador que ya venias incrementando en tu escena- y lo
    envuelve (modulo) dentro de world_w/world_h para que el scroll
    sea infinito. Para que el mosaico no se note, world_w/world_h
    deberian ser al menos del tamaño de tu pantalla (por eso el
    __init__ pide w_scr/h_scr).
    """

    def __init__(self, w_scr, h_scr, cell=18, threshold=0.9, noise_scale=0.12,
                 min_size=1, max_size=3, color=(255, 255, 255), margin=64, seed=0):
        self.world_w = w_scr + margin
        self.world_h = h_scr + margin
        self.color = color

        noise = noise2()
        rng = random.Random(seed)

        self.stars = []  # cada item: (x, y, size, brillo 0..1, profundidad)
        gy = 0.0
        while gy < self.world_h:
            gx = 0.0
            while gx < self.world_w:
                jx = gx + rng.uniform(0, cell)
                jy = gy + rng.uniform(0, cell)

                n = noise.noise2d(jx * noise_scale, jy * noise_scale)
                if n > threshold:
                    t = min(1.0, (n - threshold) / max(1e-6, 1.0 - threshold))
                    size = min_size + t * (max_size - min_size)
                    bright = 0.35 + t * 0.65
                    depth = 0.35 + t * 0.65  # mas brillante/grande = "mas cerca" = se mueve mas rapido
                    self.stars.append((jx, jy, size, bright, depth))

                gx += cell
            gy += cell

    def draw(self, screen, ox, oy):
        sw, sh = screen.get_width(), screen.get_height()
        r, g, b = self.color
        ww, wh = self.world_w, self.world_h
        margin = 4

        for x, y, size, bright, depth in self.stars:
            bx = (x - ox * depth) % ww
            by = (y - oy * depth) % wh
            color = (int(r * bright), int(g * bright), int(b * bright))
            isize = max(1, round(size))

            for sx in (bx, bx - ww):
                if -margin <= sx <= sw + margin:
                    for sy in (by, by - wh):
                        if -margin <= sy <= sh + margin:
                            pygame.draw.circle(screen, color, (int(sx), int(sy)), isize)
            
        