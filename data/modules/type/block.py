import pygame

from data.modules.services.spr_manager import spr_manager
from data.modules.type.types.entities import player
from data.modules.type.item import item


class block:
    def __init__(self, name: str, x: int, y: int, size: tuple, color: tuple, spr: pygame.Surface=None):
        """Clase padre para diferentes tipos de bloques.

        Args:
            name (str): Nombre de cada instancia
            x (int): Posición en x
            y (int): Posición en y
            size (tuple): Tamaño en (ancho, alto)
            color (tuple): Color (r, g, b)
            spr (pygame.Surface): Sprite del bloque
        """
        self.name = name
        self.color = color
        self.w = size[0]
        self.h = size[1]
        self.y = y
        self.x = x

        try:
            self.spr = spr
            self.rect = self.spr.get_rect()
            self.rect.topleft = (x, y)

            self.sprite_active = True
        
        except:
            print("No fue posible cargar sprite!")

            self.surf = pygame.Surface((size[0], size[1]))
            self.surf.fill(color)
            self.rect = self.surf.get_rect()
            self.rect.topleft = (x, y)  

            self.sprite_active = False                

    def draw(self, screen):
        if self.sprite_active:
            screen.blit(self.spr, self.rect)
        else:
            screen.blit(self.surf, self.rect)


class harvestable_block(block):
    def __init__(self, name, x, y, size, color, tool=None, spr=None, hardness=0, ore_amount=3200):
        super().__init__(name, x, y, size, color, spr)
        self.tool = tool
        self.hardness = hardness
        self.ore_amount = ore_amount

    def check_collide(self, plr: player):
        if self.active:
            if self.rect.colliderect(plr.rect):
                return True
            return None
        return None

    def destroy(self):
        self.active = False
        if self.sprite:
            del self.sprite
            self.sprite = None

    def check_ore_amount(self):
            if self.ore_amount:
                print(self.ore_amount, "items de: ", self.name)
                return self.ore_amount
            return 0

