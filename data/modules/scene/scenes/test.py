from ..scene import scene
from settings import *
from data.modules.type.stellar_obj import *


class test(scene):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.Font(None, 34)
        self.text = "Ingrese"
        win_size = game.screen.get_size()
        print(win_size)

        self.planet = planet(150, 300, 6.37, (255, 0, 0), 5.97e24)
        self.star = star(512 + 32*5, 320 - 16, 695, (200, 200, 10), 1.98e30, 100)

    def events(self, event):
        pass
        # if event.type == pygame.KEYUP:
            # if event.key == pygame.K_j:
                # self.game.set_scene("game")

    def update(self):
        self.planet.orbit(self.star, 440, 0.008, -150, orbit_ry=0)

    def draw(self, screen):
        screen.fill(white)

        self.star.draw(screen, 0.3)
        self.planet.draw(screen, 5.5)
