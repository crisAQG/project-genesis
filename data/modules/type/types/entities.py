import pygame, random
from pygame import Vector2

from data.modules.services.gui import text, img_button
from data.modules.type.entity import Entity
from data.modules.services.inventory import inventory
from settings import *
from .items import load_items


class player(Entity):
    def __init__(self, game, scene, worldx, worldy, size, scale, hp, dmg, speed, sprint_boost, shield, color, spr, sx, sy, is_flying=False):
        super().__init__(worldx, worldy, size, scale, hp, speed, dmg, shield, color, spr, sx, sy, is_flying)
        self.game = game
        self.scene = scene

        # Crea la UI del inventario
        self.inventory = inventory(game)
        self.sprint = sprint_boost
        
        starter_i = load_items()

        self.inventory.add_item(starter_i.get("stone-pickaxe"), 32)
        self.inventory.add_item(starter_i.get("stone-axe"), 32)
        self.inventory.add_item(starter_i.get("stone-sword"), 32)

        self.active_inventory = False
        self.e_pressed = False
        self.esc_pressed = False
        self.f_pressed = False
       
    def movement(self):
        self.position += self.velocity

    def attack(self):
        self.harvest()

    def harvest(self, tool=None, power=None, radius=40):
        if tool is None:
            tool = self.inventory._active_slot()
        if power is None:
            power = getattr(tool, "power", 1)

        _chunk, prop = self.scene.world.get_prop_at_world(
            self.position.x, self.position.y, radius=radius)

        if prop is None:
            return False

        self.inventory.decrease_slot_amount(1, self.inventory._find_active_slot())

        drops = prop.interact(tool=tool, power=power)
        if drops is not None:
            _chunk.mark_prop_destroyed(prop)
            self._collect_drops(drops)

        return True

    def _collect_drops(self, drops):
        for item, amount in drops:
            self.inventory.add_item(item, amount)

    def keyboard_commands(self):
        keys = pygame.key.get_pressed()
        self.velocity = Vector2(0, 0)

        if keys[pygame.K_e] and not self.e_pressed:
            self.active_inventory = not self.active_inventory
            self.inventory.appear(self.active_inventory)
            self.e_pressed = True

        if not keys[pygame.K_e]:
            self.e_pressed = False

        if keys[pygame.K_f] and not self.f_pressed:
            self.harvest()
            self.f_pressed = True

        if not keys[pygame.K_f]:
            self.f_pressed = False

        if keys[pygame.K_a]:
            self.velocity.x = -self.speed
        if keys[pygame.K_d]:
            self.velocity.x = self.speed
        if keys[pygame.K_w]:
            self.velocity.y = -self.speed
        if keys[pygame.K_s]:
            self.velocity.y = self.speed

        if keys[pygame.K_a] and (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]):
            self.velocity.x = -self.speed * self.sprint
        if keys[pygame.K_d] and (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]):
            self.velocity.x = self.speed * self.sprint
        if keys[pygame.K_w] and (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]):
            self.velocity.y = -self.speed * self.sprint
        if keys[pygame.K_s] and (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]):
            self.velocity.y = self.speed * self.sprint

        if self.velocity.x != 0 and self.velocity.y != 0:
            self.velocity *= 0.7071 

    def update(self):
        self.keyboard_commands()   
        self.rotate(self.velocity)

        self.movement()

        self.inventory.update()
        self.inventory.event()

        self.rect.center = self.position

    def draw(self, camera, screen):
        screen.blit(self.image, camera.apply(self))


class npc(Entity):
    def __init__(self, worldx, worldy, size, scale, hp, dmg, speed, shield, color, spr, sx, sy, is_flying=False):
        
        super().__init__(worldx, worldy, size, scale, hp, speed, dmg, shield, color, spr, sx, sy, is_flying)

    def update(self):
        self.rect.center = self.position

    def draw(self, camera, screen):
        screen.blit(self.image, camera.apply_rect(self.rect))