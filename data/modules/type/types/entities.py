import pygame
from pygame import Vector2

from data.modules.services.gui import text, img_button
from data.modules.type.entity import Entity
from data.modules.services.inventory import inventory
from settings import *


class player(Entity):
    def __init__(self, game, scene, worldx, worldy, size, scale, hp, dmg, speed, sprint_boost, shield, color, spr, sx, sy, is_flying=False):
        super().__init__(worldx, worldy, size, scale, hp, speed, dmg, shield, color, spr, sx, sy, is_flying)
        self.game = game
        self.scene = scene

        # Crea la UI del inventario
        self.inventory = inventory(game)
        self.sprint = sprint_boost

        self.active_inventory = False
        self.e_pressed = False
        self.esc_pressed = False
       
    def movement(self):
        self.position += self.velocity

    def attack(self):
        pass

    def keyboard_commands(self):
        keys = pygame.key.get_pressed()
        self.velocity = Vector2(0, 0)

        if keys[pygame.K_e] and not self.e_pressed:
            self.active_inventory = not self.active_inventory
            self.inventory.appear(self.active_inventory)
            self.e_pressed = True

        if not keys[pygame.K_e]:
            self.e_pressed = False

        """if keys[pygame.K_ESCAPE] and (not self.esc_pressed and (self.e_pressed == False)):
            self.esc_pressed = True
            do = True
            for i in self.menu:
                if do:
                    do = not do
                    #i.move_to(i.x + self.game.screen.get_width(), i.y)
                else:
                    #i.move_to(i.x - self.game.screen.get_width(), i.y)
                    pass

        if not keys[pygame.K_ESCAPE]:
            self.esc_pressed = False"""

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

        #for i in self.menu:
            #i.update_movement()
            #and (self.esc_pressed == False)
        
        self.rect.center = self.position

    def draw(self, camera, screen):
        screen.blit(self.image, camera.apply(self))
        self.inventory.draw(screen)
        #for i in self.menu:
            #i.draw(screen)
            


class npc(Entity):
    def __init__(self, worldx, worldy, size, scale, hp, dmg, speed, shield, color, spr, sx, sy, is_flying=False):
        
        super().__init__(worldx, worldy, size, scale, hp, speed, dmg, shield, color, spr, sx, sy, is_flying)

    def update(self):
        self.rect.center = self.position

    def draw(self, camera, screen):
        screen.blit(self.image, camera.apply_rect(self.rect))