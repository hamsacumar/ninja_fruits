import cv2
import numpy as np
import random


class SplatterManager:
    """
    Keeps a persistent juice-splatter layer over the webcam frame, like
    drops on a camera lens. Each slice adds a few blobs + drips in the
    fruit's juice color; the whole layer slowly fades over a few seconds.
    """

    def __init__(self, width, height, decay=0.985):
        self.canvas = np.zeros((height, width, 3), dtype=np.uint8)
        self.alpha = np.zeros((height, width), dtype=np.uint8)
        self.decay = decay

    def splash(self, x, y, color, blobs=6, spread=40):
        for _ in range(blobs):
            ox = x + random.randint(-spread, spread)
            oy = y + random.randint(-spread, spread)
            r = random.randint(8, 22)
            cv2.circle(self.canvas, (int(ox), int(oy)), r, color, -1, cv2.LINE_AA)
            cv2.circle(self.alpha, (int(ox), int(oy)), r, 160, -1, cv2.LINE_AA)

        # a few drips running "down" the lens
        for _ in range(max(1, blobs // 2)):
            ox = x + random.randint(-spread, spread)
            oy = y + random.randint(0, spread * 2)
            ax, ay = 3, random.randint(10, 25)
            cv2.ellipse(self.canvas, (int(ox), int(oy)), (ax, ay), 0, 0, 360,
                        color, -1, cv2.LINE_AA)
            cv2.ellipse(self.alpha, (int(ox), int(oy)), (ax, ay), 0, 0, 360,
                        130, -1, cv2.LINE_AA)

    def update(self):
        self.alpha = (self.alpha.astype(np.float32) * self.decay).astype(np.uint8)

    def apply(self, frame):
        if self.alpha.shape[:2] != frame.shape[:2]:
            return  # camera resolution changed mid-run, skip safely
        a = (self.alpha.astype(np.float32) / 255.0)[:, :, None]
        blended = frame.astype(np.float32) * (1 - a) + self.canvas.astype(np.float32) * a
        frame[:] = blended.astype(np.uint8)

    def clear(self):
        self.canvas[:] = 0
        self.alpha[:] = 0