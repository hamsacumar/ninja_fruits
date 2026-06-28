import random

# Each entry defines the look of one fruit type.
# Colors are in BGR (OpenCV order).
FRUIT_TYPES = [
    {
        "name": "apple",
        "skin_light": (70, 70, 235),
        "skin_dark": (35, 25, 140),
        "highlight": (200, 200, 255),
        "leaf": (50, 150, 50),
        "stem": (40, 70, 95),
        "juice": (60, 60, 220),
    },
    {
        "name": "orange",
        "skin_light": (40, 150, 250),
        "skin_dark": (15, 95, 190),
        "highlight": (160, 210, 255),
        "leaf": (50, 150, 50),
        "stem": (40, 70, 95),
        "juice": (30, 140, 250),
    },
    {
        "name": "watermelon",
        "skin_light": (70, 170, 60),
        "skin_dark": (25, 100, 25),
        "highlight": (170, 230, 170),
        "leaf": (50, 150, 50),
        "stem": (40, 70, 95),
        "juice": (60, 50, 220),
        "stripe": (15, 80, 15),
    },
    {
        "name": "lime",
        "skin_light": (60, 200, 110),
        "skin_dark": (30, 140, 55),
        "highlight": (170, 235, 190),
        "leaf": (50, 150, 50),
        "stem": (40, 70, 95),
        "juice": (60, 200, 110),
    },
]


class Fruit:
    def __init__(self, width, height):
        self.x = random.randint(100, width - 100)
        self.y = height
        self.radius = random.randint(28, 38)
        self.vx = random.randint(-3, 3)
        self.vy = -15
        self.angle = random.uniform(0, 360)   # current rotation, for sprite drawing
        self.spin = random.uniform(-3, 3)     # degrees per frame
        self.type = random.choice(FRUIT_TYPES)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.5
        self.angle += self.spin