import pygame

from settings import *
from data.modules.scene.scenes import main_menu, test, game
from data.modules.services.spr_manager import spr_manager


class window:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1366, 768), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()

        self.running = True
        self.running = True

        self.font = pygame.font.Font(None, size=16)
        self.gui = spr_manager("data/sprites/gui.png")

        self.world_data = ["", "", 0]

        self.scene_map = {
            "test": lambda: test.test(self),
            "main menu": lambda: main_menu.main_menu(self),
            "game": lambda: game.game(self, self.world_data),
            #"world_creator": lambda: wrld_creator_menu(self),
            #"world": lambda: world(self)
        }

        self.scene = self.scene_map["main menu"]()

    def set_scene(self, scene_name: str, data=None):
        """Cambiar escena con parámetros opcionales"""
        if scene_name in self.scene_map:
            if scene_name == "game" and data is not None:
                self.world_data = data
            self.scene = self.scene_map[scene_name]()

    def events(self):
        for events in pygame.event.get():
            if events.type == pygame.QUIT:
                self.running = False
            if self.scene:
                self.scene.events(events)

    def update(self):
        if self.scene:
            self.scene.update()

    def draw(self):
        self.screen.fill((0, 0, 0))
        if self.scene:
            self.scene.draw(self.screen)

    def loop(self):
        while self.running:
            self.clock.tick(fps)
            self.events()
            self.update()
            self.draw()
            pygame.display.flip()
