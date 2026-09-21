import pygame

from data.modules.services.spr_manager import spr_manager


class item:
    def __init__(self, name: str, x: int, y: int, size: int, color: tuple, spr:pygame.Surface, sx, sy):
        self.name = name
        self.y = y
        self.x = x
        self.size = size

        try:
            self.spr = spr_manager(spr).get_sprite(sx, sy, size, size)
            self.rect = self.spr.get_rect()
            self.rect.topleft = (x, y)  
            self.active_sprite = True

        except:
            self.surf = pygame.Surface((size, size))
            self.surf.fill(color)
            self.rect = self.surf.get_rect()
            self.rect.topleft = (x, y)
            self.active_sprite = False

    def draw(self, screen):
        if self.active_sprite:
            screen.blit(self.spr, self.rect)
        else:
            screen.blit(self.surf, self.rect)


class tool(item):
    def __init__(self, name, x, y, size, color, power, lifespan, spr:pygame.Surface=None, amount=0):
        super().__init__(name, x, y, size, color, spr, amount)
        self.life = lifespan
        self.power = power