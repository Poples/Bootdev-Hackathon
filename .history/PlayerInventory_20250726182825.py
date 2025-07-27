

class Inventory:
    def __init__(self):
        self.items = []
  
    def add_item(self, item):
        self.items.append(item)
        
    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)

class Item:
    def __init__(self, name, description):
        self.name = name
        self.description = description