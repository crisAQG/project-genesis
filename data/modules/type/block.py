import pygame
import random
import copy

from .item import axe, pickaxe


class block:
    def __init__(self, name: str, world_x: int, world_y: int, color: tuple, spr: pygame.Surface=None):
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
        self.world_x = world_x
        self.world_y = world_y

        try:
            self.spr = spr
            self.rect = self.spr.get_rect()
            self.rect.topleft = (self.world_x, self.world_y)

            self.sprite_active = True
        
        except:
            print("No fue posible cargar sprite!")

            self.surf = pygame.Surface((32, 32))
            self.surf.fill(color)
            self.rect = self.surf.get_rect()
            self.rect.topleft = (self.world_x, self.world_y)  

            self.sprite_active = False    

    def set_pos(self, x, y):
        self.world_x = x
        self.world_y = y
        self.rect.topleft = (self.world_x, self.world_y)

    def clone(self):
        """
        Copia independiente de este bloque: mismo sprite (se comparte,
        es de solo lectura), pero con su propio rect/estado. Hace
        falta para colocar varias instancias del mismo prop en el
        mundo sin que todas apunten al mismo objeto (ver blocks.py,
        donde load_blocks() crea UN solo tree/bush/mineral por tipo).
        """
        new = copy.copy(self)
        new.rect = self.rect.copy()
        return new

    def draw(self, screen):
        if self.sprite_active:
            screen.blit(self.spr, self.rect)
        else:
            screen.blit(self.surf, self.rect)


class harvestable_block(block):
    draw_layer = "ground"

    def __init__(self, name, world_x, world_y, color, hp=1,
                 tool_required=None, drops=None, spr = None):
        super().__init__(name, world_x, world_y, color, spr)
        self.hp = hp
        self.max_hp = hp
        self.tool_required = tool_required
        self.drops = drops or []

        self.active = True

        self.grid_pos = None

    def can_interact(self, tool=None):
        if not self.active:
            return False
        if self.tool_required is None:
            return True
        return isinstance(tool, self.tool_required)

    def interact(self, tool=None, power=1):
        if not self.can_interact(tool):
            return None

        self.hp -= power
        if self.hp <= 0:
            self.active = False
            return self._roll_drops()
        return None

    def _roll_drops(self):
        result = []
        for item, mn, mx in self.drops:
            amount = random.randint(mn, mx)
            if amount > 0:
                result.append((item, amount))
        return result

    def clone(self):
        new = super().clone()
        new.hp = self.max_hp
        new.active = True
        new.grid_pos = None
        return new

    def draw(self, camera, screen):
        if not self.active:
            return
        if self.sprite_active:
            screen.blit(self.spr, camera.apply_rect(self.rect))
        else:
            screen.blit(self.surf, camera.apply_rect(self.rect))


class tree(harvestable_block):
    draw_layer = "canopy"

    def __init__(self, name, world_x, world_y, color, sprite, hp=3,
                 tool_required=axe, drops=None):
        super().__init__(name,
            world_x, world_y, color,
            hp, tool_required,
            drops=drops or [("madera", 2, 5)], spr=sprite
        )


class bush(harvestable_block):
    def __init__(self, name, world_x, world_y, color, sprite, hp=3,
                 tool_required=axe, drops=None):
        super().__init__(name,
            world_x, world_y, color,
            hp, tool_required=tool_required,
            drops=drops, spr=sprite
        )


class mineral(harvestable_block):
    def __init__(self, name, world_x, world_y, color, sprite, hp=5,
                 tool_required=pickaxe, drops=None):
        super().__init__(name,
            world_x, world_y, color,
            hp, tool_required=tool_required,
            drops=drops, spr=sprite
        )