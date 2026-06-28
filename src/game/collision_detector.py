import math


class CollisionDetector:
    def check(self, fruit, blade_points):
        hit, _ = self.check_with_angle(fruit, blade_points)
        return hit

    def check_with_angle(self, fruit, blade_points):
        """
        Same hit test as before, but also returns the angle (degrees) of
        the blade segment that caused the hit, so the caller can slice
        the fruit along the actual swipe direction. Returns (False, None)
        if there's no hit.
        """
        for i in range(1, len(blade_points)):
            p1 = blade_points[i - 1]
            p2 = blade_points[i]

            steps = 5
            for t in range(steps):
                x = int(p1[0] + (p2[0] - p1[0]) * t / steps)
                y = int(p1[1] + (p2[1] - p1[1]) * t / steps)

                dist = ((fruit.x - x) ** 2 + (fruit.y - y) ** 2) ** 0.5

                if dist < fruit.radius:
                    angle = math.degrees(math.atan2(p2[1] - p1[1], p2[0] - p1[0]))
                    return True, angle

        return False, None