import sys
import pygame

from data.modules.window import window

if __name__ == '__main__':
    g = window()
    g.loop()

    pygame.quit()
    sys.exit()