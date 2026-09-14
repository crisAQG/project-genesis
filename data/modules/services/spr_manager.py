import pygame


class spr_manager:
    def __init__(self, file):
        try:
            self.sheet = pygame.image.load(file).convert_alpha()
            print(f"✅ Spritesheet cargado: {file}")
        except Exception as e:
            print(f"❌ Error cargando spritesheet: {file} - {e}")
            self.sheet = pygame.Surface((1, 1))

    def get_sprite(self, x, y, w, h):
        sprite = pygame.Surface([w, h], pygame.SRCALPHA)  # Soporte para transparencia
        sprite.blit(self.sheet, (0, 0), (x, y, w, h))
        if sprite.get_width() == 0 or sprite.get_height() == 0:
            print(f"❗ Sprite vacío: x={x}, y={y}, w={w}, h={h}")
        return sprite