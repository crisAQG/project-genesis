from data.modules.states.properties import *
from data.modules.type.item import item

class wood(item, flamable):
    def __init__(self, name, x, y, size, color, spr = None, amount=0):
        super().__init__(name, x, y, size, color, spr, amount)
        