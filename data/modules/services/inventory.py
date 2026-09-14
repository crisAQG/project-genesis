class inventory:
    def __init__(self):
        self.slots = {}
        for s in range(32):
            self.slots[s] = None
        print(self.slots)

    def add(self, item, slot):
        self.slot[slot] = item

inventory()
