import numpy as np
from collections import deque

class MotionPredictor:
    def __init__(self, size=5):
        self.points = deque(maxlen=30)

    def update(self, point):
        if point:
            if len(self.points) > 0:
                last = self.points[-1]

                # fill gap between frames
                steps = 3
                for i in range(1, steps):
                    x = int(last[0] + (point[0] - last[0]) * i / steps)
                    y = int(last[1] + (point[1] - last[1]) * i / steps)
                    self.points.append((x, y))

            self.points.append(point)

        if len(self.points) > 30:
            self.points.popleft()

    def smooth(self):
        if len(self.points) < 2:
            return None

        x = [p[0] for p in self.points]
        y = [p[1] for p in self.points]

        return (int(np.mean(x)), int(np.mean(y)))

    def predict_next(self):
        if len(self.points) < 3:
            return None

        (x1, y1), (x2, y2) = self.points[-2], self.points[-1]

        vx = x2 - x1
        vy = y2 - y1

        return (x2 + vx * 2, y2 + vy * 2)