from entities.particle import Particle


class ParticleManager:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, count=5, color=(0, 200, 255)):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def update(self):
        for p in self.particles:
            p.update()

        self.particles = [p for p in self.particles if p.life > 0]