import time


class Blade:
    def __init__(self, max_age=1, max_length=20):
        self.points = []
        self._timestamps = []
        self.last_point = None

        self.max_age = max_age        # seconds a point is allowed to live in the trail
        self.max_length = max_length  # hard cap, just as a safety net

    def update(self, point):
        now = time.time()

        if point:
            if self.last_point is None:
                self.last_point = point
            else:
                dx = point[0] - self.last_point[0]
                dy = point[1] - self.last_point[1]
                speed = (dx * dx + dy * dy) ** 0.5

                # ONLY register real sword swing
                if speed > 5:
                    self.points.append(point)
                    self._timestamps.append(now)

                self.last_point = point

        # age out old points so the trail vanishes quickly once the hand
        # slows down or stops, instead of hanging around on screen
        while self._timestamps and now - self._timestamps[0] > self.max_age:
            self._timestamps.pop(0)
            self.points.pop(0)

        # absolute cap as a safety net
        if len(self.points) > self.max_length:
            overflow = len(self.points) - self.max_length
            self.points = self.points[overflow:]
            self._timestamps = self._timestamps[overflow:]

    def clear(self):
        self.points.clear()
        self._timestamps.clear()
        self.last_point = None