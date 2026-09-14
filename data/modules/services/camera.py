import pygame
from pygame.math import Vector2

from settings import *


class camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.zoom = 1.0
        self.MIN_ZOOM = 0.5
        self.MAX_ZOOM = 2.0
        self.offset = Vector2(0, 0)

    def apply(self, entity):
        return entity.rect.move(-self.offset.x, -self.offset.y)

    def apply_rect(self, rect):
        return rect.move(-self.offset.x, -self.offset.y)

    def update(self, target):
        dx = target.rect.centerx - self.camera.centerx
        dy = target.rect.centery - self.camera.centery
        self.camera.x += dx * 0.2
        self.camera.y += dy * 0.2

        # ACTUALIZA EL OFFSET
        self.offset = pygame.Vector2(self.camera.topleft)

    def zoom_in(self):
        self.zoom = min(self.MAX_ZOOM, self.zoom * 1.1)

    def zoom_out(self):
        self.zoom = max(self.MIN_ZOOM, self.zoom / 1.1)

    def get_scaled_surface(self, surface):
        scaled_size = Vector2(surface.get_size()) * self.zoom
        return pygame.transform.scale(surface, scaled_size)