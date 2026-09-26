from data.modules.services.gui import slot, text


class inventory:
    def __init__(self, game):
        self.game = game

        self.slots = {}
        self.gui = game.gui

        self.slot = self.gui.get_sprite(32*2, 0, 32, 32)
        self.new_slot = self.gui.get_sprite(0, 0, 32, 32)
        self.actual_slot = self.gui.get_sprite(0, 0, 32, 32)
        self.special_slot = self.gui.get_sprite(32, 0, 32, 32)

        self.inv_title = text(32, 32 - game.screen.get_height(), "Inventory", game.font, scale=2)
        for i in range(32):
            row = i // 8
            col = i % 8
            x = col * 64 + 32
            y = row * 64
            self.slots[i] = slot(x, y, self.slot, 32, 32, None, 0, 2, game.font, (255, 255, 255))
            self.slots[i].set_pos(x, y - game.screen.get_height())

        self.title = text(32, 32, "Slots", game.font, scale=2)
        for i in range(8):
            self.slots[i].set_pos(i * 64 + 32, 64)

        self.active_slot = [i == 0 for i in range(32)]

    def add_item(self, item, amount):
        """
        Apila en slots que ya tengan ESE item (hasta 100 por slot) y
        recién después abre slots vacíos con lo que sobre. Devuelve lo
        que no entró (0 si entró todo) por si el inventario está lleno.
        """
        remaining = amount

        for s in self.slots.values():
            if remaining <= 0:
                break
            if s.item is item and s.amount < 100:
                add_now = min(100 - s.amount, remaining)
                s.change_amount(add_now)
                remaining -= add_now

        while remaining > 0:
            slot_id = self._find_empty_slot()
            if slot_id is None:
                break
            s = self.slots[slot_id]
            add_now = min(100, remaining)
            s.add_item(item)
            s.change_amount(add_now)
            remaining -= add_now

        return remaining

    def decrease_slot_amount(self, amount, slot):
        self.slots[slot].change_amount(-amount)

    def appear(self, do):
        if do:
            self.inv_title.move_to(self.inv_title.x, self.inv_title.y + self.game.screen.get_height())
        else:
            self.inv_title.move_to(self.inv_title.x, self.inv_title.y - self.game.screen.get_height())

        for i, slot in self.slots.items():
            if i < 8:
                continue  # hotbar: siempre visible, no se mueve

            if do:
                slot.move_to(slot.x, slot.y + self.game.screen.get_height())
            else:
                slot.move_to(slot.x, slot.y - self.game.screen.get_height())
    
    def event(self):
        for i in range(32):
            if self.slots[i].event():
                self.active_slot = [False] * 32
                self.active_slot[i] = True
                self.slots[i].sprite = self.actual_slot
                self.slots[i].update_img()
            if self.active_slot[i] == False:
                self.slots[i].sprite = self.slot
                self.slots[i].update_img()

    def _active_slot(self):
        item = None
        for i in range(32):
            if self.active_slot[i]: 
                item = self.slots[i].item
                return item
        return item

    def _find_active_slot(self):
        item = None
        for i in range(32):
            if self.active_slot[i]: 
                return i
        return None

    def _find_empty_slot(self):
        for i in range(32):
            if self.slots[i].item is None:
                return i
        return None

    def update(self):
        self.inv_title.update_movement()
        self.title.update_movement()
        for slot in self.slots.values():
            slot.update_movement()

    def draw(self, camera, screen):
        self.inv_title.draw(screen)
        self.title.draw(screen)
        for slot in self.slots.values():
            slot.draw(camera, screen)