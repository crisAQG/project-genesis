from data.modules.scene.scene import scene
from data.modules.services.map_gen import map_gen
from data.modules.services.camera import camera
from data.modules.type.types.entities import player, npc
from settings import *


class game(scene):
    def __init__(self, game, world_data):
        super().__init__(game)
        self.inicio = pygame.time.get_ticks()

        self._w_data = world_data

        self.world = map_gen(world_data[2])

        sp_x, sp_y = self._find_spawn(self.world)

        self.npc = npc(sp_x, sp_y, 32, 1, (0, 0, 0))

        self.plr = player(self.game, self, sp_x, sp_y, 32, 1, 100, 0, 5, 0.2, 0, (255, 0, 0), "data\sprites\Player.png")
        self.camera = camera(game.screen.get_width(), game.screen.get_height())

    def events(self, event):
        pass

    def _find_spawn(self, world, max_radius=64):
        for r in range(max_radius):
            for dx in range(-r, r, 1):
                for dy in range(-r, r, 1):
                    wx = dx*32*2
                    wy = dy*32*2

                    if world.is_walkable(wx, wy):
                        return wx, wy
        return 0, 0

    def update(self):
        self.ahora = pygame.time.get_ticks()

        self.npc.update()
    
        self.npc.random_patrol(self.world.is_walkable, 128, 2.5, self)
        
        self.plr.update()
        self.camera.update(self.plr)
        self.world.update(self.plr)

    def draw(self, screen):
        self.world.draw(self.camera, screen)
        self.npc.draw(screen, self.camera)
        self.plr.draw(self.camera, screen)