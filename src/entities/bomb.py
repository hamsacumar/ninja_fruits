import random


class Bomb:
    def __init__(self, width, height):
        self.x = random.randint(100, width - 100)
        self.y = height
        self.radius = 32
        self.vx = random.randint(-3, 3)
        self.vy = -15

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.5