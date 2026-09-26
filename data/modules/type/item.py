import pygame

from data.modules.services.spr_manager import spr_manager


class item:
    def __init__(self, name: str, x: int, y: int, size: int, color: tuple, spr:pygame.Surface, amount=0):
        self.name = name
        self.y = y
        self.x = x
        self.size = size
        self.amount = amount

        self.is_drop = False

        try:
            self.spr = spr
            self.rect = self.spr.get_rect()
            self.rect.topleft = (self.x, self.y)  
            self.active_sprite = True

        except:
            self.surf = pygame.Surface((size, size))
            self.surf.fill(color)
            self.rect = self.surf.get_rect()
            self.rect.topleft = (self.x, self.y)
            self.active_sprite = False

    def set_pos(self, x, y):
        self.x = x
        self.y = y
        self.rect.topleft = (self.x, self.y)

    def draw(self, camera, screen):
        if self.is_drop: 
            if self.active_sprite:
                screen.blit(self.spr, camera.apply_rect(self.rect))
            else:
                screen.blit(self.surf, camera.apply_rect(self.rect))
        else:
            if self.active_sprite:
                screen.blit(self.spr, self.rect)
            else:
                screen.blit(self.surf, self.rect)


class tool(item):
    def __init__(self, name, x, y, size, color, power, lifespan, spr:pygame.Surface=None):
        super().__init__(name, x, y, size, color, spr, lifespan)
        self.life = lifespan
        self.power = power

class weapon(item):
    def __init__(self, name, x, y, size, color, dmg, lifespan, spr = None):
        super().__init__(name, x, y, size, color, spr, lifespan)
        self.life = lifespan
        self.dmg = dmg

class pickaxe(tool):
    def __init__(self, name, x, y, size, color, power, lifespan=0, spr = None):
        super().__init__(name, x, y, size, color, power, lifespan, spr)

class axe(tool):
    def __init__(self, name, x, y, size, color, power, lifespan=0, spr = None):
        super().__init__(name, x, y, size, color, power, lifespan, spr)

class sword(weapon):
    def __init__(self, name, x, y, size, color, dmg, lifespan=0, spr=None):
        super().__init__(name, x, y, size, color, dmg, lifespan, spr)

############
# PICKAXES #
############

class stone_pickaxe(pickaxe):
    def __init__(self, name, x, y, size, color, power, lifespan=0, spr = None):
        super().__init__(name, x, y, size, color, power, lifespan, spr)

class copper_pickaxe(pickaxe):
    def __init__(self, name, x, y, size, color, power, lifespan=0, spr = None):
        super().__init__(name, x, y, size, color, power, lifespan, spr)

########
# AXES #
########

class stone_axe(axe):
    def __init__(self, name, x, y, size, color, power, lifespan=0, spr = None):
        super().__init__(name, x, y, size, color, power, lifespan, spr)

class copper_axe(axe):
    def __init__(self, name, x, y, size, color, power, lifespan=0, spr = None):
        super().__init__(name, x, y, size, color, power, lifespan, spr)

##########
# SWORDS #
##########

class stone_sword(sword):
    def __init__(self, name, x, y, size, color, dmg, lifespan=0, spr = None):
        super().__init__(name, x, y, size, color, dmg, lifespan, spr)

class copper_sword(sword):
    def __init__(self, name, x, y, size, color, dmg, lifespan=0, spr = None):
        super().__init__(name, x, y, size, color, dmg, lifespan, spr)