from data.modules.services.gui import slot, text


class inventory:
    def __init__(self, game):
        self.game = game

        self.slots = {}
        self.gui = game.gui

        self.title = text(32, 32 - game.screen.get_height(), "Inventory", game.font, scale=2)
        for i in range(32):
            row = i // 8
            col = i % 8

            x = col * 64 + 32
            y = row * 64 + 80

            self.slots[i] = slot(x, y, self.gui, 32*2, 0, 32, 32, None, 0, 2, game.font, (255, 255, 255))
            self.slots[i].set_pos(x, y - game.screen.get_height())

        # self.new_slot = img_button(0, 0, self.gui, 0, 0, 32, 32, 2)
        # self.special_slot = img_button(0, 0, self.gui, 32, 0, 32, 32, 2)

    def add_item(self, item, amount, slot):
        self.slots[slot].change_amount(amount)
        self.slots[slot].add_item(item)

    def decrease_slot_amount(self, amount, slot):
        self.slots[slot].change_amount(amount)

    def appear(self, do):
        if do:
            self.title.move_to(self.title.x, self.title.y + self.game.screen.get_height())
        else:
            self.title.move_to(self.title.x, self.title.y - self.game.screen.get_height())

        for slot in self.slots.values():
            if do:
                slot.move_to(slot.x, slot.y + self.game.screen.get_height())
            else:
                slot.move_to(slot.x, slot.y - self.game.screen.get_height())

    def event(self):
        for key in self.slots:
            if key.event() == True:
                pass
    
    def update(self):
        self.title.update_movement()
        for slot in self.slots.values():
            slot.update_movement()

    def event(self):
        pass

    def draw(self, screen):
        self.title.draw(screen)
        for slot in self.slots.values():
            slot.draw(screen)