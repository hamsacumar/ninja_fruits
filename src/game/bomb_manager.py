from entities.bomb import Bomb


class BombManager:
    def __init__(self):
        self.bombs = []

    def spawn(self, w, h):
        self.bombs.append(Bomb(w, h))

    def update(self):
        for bomb in self.bombs:
            bomb.update()
        # drop ones that fell way off screen so the list doesn't grow forever
        self.bombs = [b for b in self.bombs if b.y < 3000]