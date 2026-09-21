from data.modules.scene.scene import scene
from data.modules.services.map_gen import map_gen
from data.modules.services.camera import camera
from data.modules.type.types.entities import player, npc
from data.modules.services.gui import text, img_button
from settings import *


class game(scene):
    def __init__(self, game, world_data):
        super().__init__(game)
        self.inicio = pygame.time.get_ticks()

        self._w_data = world_data

        print(world_data)

        self.world = map_gen(world_data[2])

        sp_x, sp_y = self._find_spawn(self.world)

        self.npc = npc(sp_x, sp_y, 32, 1, 100, 1, 1, 0, (0, 0, 0), "data\sprites\Player.png", 0, 0)

        self.plr = player(game, self, sp_x, sp_y, 32, 1, 100, 0, 5, 1.7, 0, (255, 0, 0), "data/sprites/Player.png", 0, 0)
        self.camera = camera(game.screen.get_width(), game.screen.get_height())

        self.text_menu = text(
                            64 - game.screen.get_width(),
                            128, "mundo", game.font, scale=2)

        self.bck_menu = img_button(
                            64 - game.screen.get_width(),
                            game.screen.get_height() - 64*4,
                            game.gui, 0, 32*4, 32*3, 32, 2, "Exit", game.font, (255,255,255), 0, 32*5, 16, 16)

        self.active_menu = False

    def events(self, event):
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE and self.plr.active_inventory == False:
                if not self.active_menu:
                    self.active_menu = not self.active_menu
                    self.text_menu.move_to(self.text_menu.x + self.game.screen.get_width(), self.text_menu.y)
                    self.bck_menu.move_to(self.bck_menu.x + self.game.screen.get_width(), self.bck_menu.y)
                else:
                    self.active_menu = not self.active_menu
                    self.text_menu.move_to(self.text_menu.x - self.game.screen.get_width(), self.text_menu.y)
                    self.bck_menu.move_to(self.bck_menu.x - self.game.screen.get_width(), self.bck_menu.y)
        if self.bck_menu.event():
            self.game.set_scene("main menu")

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
    
        self.npc.random_patrol(self, 32, 32)
        
        self.plr.update()
        self.camera.update(self.plr)
        self.world.update(self.plr)

        self.text_menu.update_movement()
        self.bck_menu.update_movement()

    def draw(self, screen):
        self.world.draw(self.camera, screen)
        self.npc.draw(self.camera, screen)
        self.plr.draw(self.camera, screen)

        self.text_menu.draw(screen)
        self.bck_menu.draw(screen)