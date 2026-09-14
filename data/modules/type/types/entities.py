import pygame
from pygame import Vector2

from data.modules.services.spr_manager import spr_manager
from data.modules.type.entity import entity
from data.modules.services.inventory import inventory
from settings import *


class player(entity):
    def __init__(self, game, scene, worldx, worldy, size, scale, hp, dmg, speed, sprint_boost, shield, color, image, is_flying=False):
        super().__init__(worldx, worldy, size, scale, color, is_flying)
        self.game = game
        self.scene = scene

        # Crea la UI del inventario
        # self.inventory = [

        # ]

        # self.inv_mgr = inventory(self.inventory)

        # Usar directamente los píxeles
        self.velocity = Vector2(0, 0)
        self.angle = 0
        self.rotation_speed = 5

        self.hp = hp
        self.speed = speed
        self.sprint = sprint_boost
        self.dmg = dmg
        self.shield = shield

        self.original_image = spr_manager(image).get_sprite(0, 0, self.size, self.size)
        self.original_image = pygame.transform.scale(self.original_image, (self.size, self.size))
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(topleft=(self.position.x, self.position.y))

    def movement(self):
        self.position += self.velocity

    def attack(self):
        pass

    def keyboard_commands(self):
        keys = pygame.key.get_pressed()
        self.velocity = Vector2(0, 0)

        if keys[pygame.K_a]:
            self.velocity.x = -self.speed
            self.target_angle = 90
        if keys[pygame.K_d]:
            self.velocity.x = self.speed
            self.target_angle = 270
        if keys[pygame.K_w]:
            self.velocity.y = -self.speed
            self.target_angle = 0
        if keys[pygame.K_s]:
            self.velocity.y = self.speed
            self.target_angle = 180

        if keys[pygame.KMOD_SHIFT]:
            if keys[pygame.K_a]:
                self.velocity.x = -self.speed * self.sprint
                self.target_angle = 90
            if keys[pygame.K_d]:
                self.velocity.x = self.speed * self.sprint
                self.target_angle = 270
            if keys[pygame.K_w]:
                self.velocity.y = -self.speed * self.sprint
                self.target_angle = 0
            if keys[pygame.K_s]:
                self.velocity.y = self.speed * self.sprint
                self.target_angle = 180

        if self.velocity.x != 0 and self.velocity.y != 0:
            self.velocity *= 0.7071 

    def rotate(self):
        if hasattr(self, 'target_angle'):
            angle_diff = (self.target_angle - self.angle) % 360
            if angle_diff > 180:
                angle_diff -= 360
            if abs(angle_diff) < self.rotation_speed:
                self.angle = self.target_angle
            else:
                self.angle += self.rotation_speed if angle_diff > 0 else -self.rotation_speed

        self.angle %= 360
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def inventory(self):
        pass

    def update(self):
        self.keyboard_commands()
        self.movement()
        self.rotate()

        self.rect.center = self.position

    def draw(self, camera, screen):
        screen.blit(self.image, camera.apply(self))
