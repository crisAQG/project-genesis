import math
import random

class noise2:
    def __init__(self, seed=None):
        if seed is None:
            self.seed = random.Random().randint(0, 100000)
        else:
            self.seed = seed
 
    def _hash(self, x, y):
        n = x * 374761393 + y * 668265263 + self.seed * 2147483647
        n = (n ^ (n >> 13)) * 1274126177
        n = n ^ (n >> 16)
        return (n & 0xFFFFFFFF) / 0xFFFFFFFF
 
    @staticmethod
    def _smoothstep(t):
        return t * t * (3 - 2 * t)
 
    def noise2d(self, x, y):
        """Ruido de valor suavizado en (x, y) -> rango [0, 1]"""
        x0, y0 = math.floor(x), math.floor(y)
        x1, y1 = x0 + 1, y0 + 1
 
        sx = self._smoothstep(x - x0)
        sy = self._smoothstep(y - y0)
 
        n00 = self._hash(x0, y0)
        n10 = self._hash(x1, y0)
        n01 = self._hash(x0, y1)
        n11 = self._hash(x1, y1)
 
        ix0 = n00 + (n10 - n00) * sx
        ix1 = n01 + (n11 - n01) * sx
        return ix0 + (ix1 - ix0) * sy
 
    def fbm(self, x, y, octaves=5, persistence=0.5, lacunarity=2.0, scale=0.02):
        """Ruido fractal (suma de octavas de noise2d) -> rango ~[0, 1]"""
        amplitude = 1.0
        frequency = 1.0
        total = 0.0
        max_amplitude = 0.0
 
        for _ in range(octaves):
            total += self.noise2d(x * scale * frequency, y * scale * frequency) * amplitude
            max_amplitude += amplitude
            amplitude *= persistence
            frequency *= lacunarity
 
        return total / max_amplitude

