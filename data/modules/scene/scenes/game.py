from data.modules.scene.scene import scene
from data.modules.services.map_gen import map_gen
from data.modules.services.camera import camera
from data.modules.type.types.entities import player
from settings import *


class game(scene):
    def __init__(self, game, world_data):
        super().__init__(game)

        self.world = map_gen()

        self.plr = player(self.game, self, 0, 0, 32, 1, 100, 0, 5, 0.2, 0, (255, 0, 0), "data\sprites\Player.png")
        self.camera = camera(game.screen.get_width(), game.screen.get_height())

    def events(self, event):
        pass

    def update(self):
        self.plr.update()
        self.camera.update(self.plr)
        self.world.update(self.plr)

    def draw(self, screen):
        self.world.draw(self.camera, screen)
        self.plr.draw(self.camera, screen)