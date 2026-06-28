class FruitHalf:
    """
    One half of a fruit after it's been sliced. Holds a pre-rendered
    RGBA sprite (already cut along the slice line) and flies off with
    its own velocity/spin, fading out near the end of its life.
    """

    def __init__(self, x, y, sprite, vx, vy, spin):
        self.x = x
        self.y = y
        self.sprite = sprite
        self.vx = vx
        self.vy = vy
        self.spin = spin
        self.angle = 0.0
        self.life = 20
        self.alpha = 1.0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.7  # falls a bit faster than a whole fruit
        self.angle += self.spin
        self.life -= 1
        if self.life < 8:
            self.alpha = max(0.0, self.life / 8)