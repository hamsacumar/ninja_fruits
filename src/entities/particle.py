import random


class Particle:
    def __init__(self, x, y, color=(0, 200, 255)):
        self.x = x
        self.y = y
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-6, -1)
        self.life = random.randint(15, 25)
        self.color = color  # BGR, matches the fruit that was sliced

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.3  # gravity
        self.life -= 1