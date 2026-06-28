from entities.fruit import Fruit


class FruitManager:
    def __init__(self):
        self.fruits = []

    def spawn(self, w, h):
        self.fruits.append(Fruit(w, h))

    def update(self):
        for fruit in self.fruits:
            fruit.update()
        # drop ones that fell way off screen so the list doesn't grow forever
        self.fruits = [f for f in self.fruits if f.y < 3000]