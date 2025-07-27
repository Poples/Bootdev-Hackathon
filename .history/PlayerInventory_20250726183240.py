

class PlayerInventory:
    def __init__(self):
        # Store items as a dictionary: {item_name: quantity}
        self.items = {}

    def add_item(self, item_name, quantity=1):
        if item_name in self.items:
            self.items[item_name] += quantity
        else:
            self.items[item_name] = quantity

    def remove_item(self, item_name, quantity=1):
        if item_name in self.items:
            self.items[item_name] -= quantity
            if self.items[item_name] <= 0:
                del self.items[item_name]
            return True
        return False  # Item not found

    def has_item(self, item_name):
        return item_name in self.items

    def get_quantity(self, item_name):
        return self.items.get(item_name, 0)

    def list_items(self):
        return self.items.copy()  # return a copy to prevent external modification