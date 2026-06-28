import cv2
import numpy as np
import math
import random


class Renderer:

    def __init__(self):
        self._fruit_sprites = {}  # cache: (fruit_name, radius) -> RGBA sprite, or "_bomb" -> (sprite, fuse_pt)

    # ---------------- BLADE ----------------

    def draw_blade(self, frame, blade):
        """
        Tapered, glowing sword slash: thin + transparent at the tail
        (older positions), thick + bright at the head (current position).
        """
        pts = self.smooth_curve(blade.points)
        n = len(pts)
        if n < 2:
            return

        overlay = np.zeros_like(frame)

        for i in range(1, n):
            t = i / (n - 1)
            thickness = max(2, int(3 + 16 * t))
            color = (
                int(255 * (0.55 + 0.45 * t)),
                int(255 * (0.75 + 0.25 * t)),
                255,
            )
            cv2.line(overlay, pts[i - 1], pts[i], color, thickness, cv2.LINE_AA)

        glow = cv2.GaussianBlur(overlay, (0, 0), 9)
        cv2.add(frame, glow, frame)

        for i in range(1, n):
            t = i / (n - 1)
            thickness = max(1, int(1 + 3 * t))
            cv2.line(frame, pts[i - 1], pts[i], (255, 255, 255), thickness, cv2.LINE_AA)

    def smooth_curve(self, points, factor=0.5):
        if len(points) < 3:
            return points

        smooth = []
        for i in range(len(points)):
            if i == 0 or i == len(points) - 1:
                smooth.append(points[i])
            else:
                x = int(
                    points[i][0] * factor +
                    (points[i - 1][0] + points[i + 1][0]) * (1 - factor) / 2
                )
                y = int(
                    points[i][1] * factor +
                    (points[i - 1][1] + points[i + 1][1]) * (1 - factor) / 2
                )
                smooth.append((x, y))
        return smooth

    # ---------------- FRUITS ----------------

    def _build_fruit_sprite(self, ftype, radius):
        pad = int(radius * 0.6) + 6
        size = radius * 2 + pad * 2
        cx, cy = size // 2, size // 2

        sprite = np.zeros((size, size, 4), dtype=np.uint8)

        for r in range(radius, 0, -1):
            f = r / radius
            light = 1 - f
            color = tuple(
                min(255, int(
                    ftype["skin_dark"][c] * f + ftype["skin_light"][c] * (1 - f) + 40 * light
                ))
                for c in range(3)
            )
            ox = int(-radius * 0.18 * (1 - f))
            oy = int(-radius * 0.18 * (1 - f))
            cv2.circle(sprite, (cx + ox, cy + oy), r, (*color, 255), -1, cv2.LINE_AA)

        if "stripe" in ftype:
            mask = np.zeros((size, size), dtype=np.uint8)
            cv2.circle(mask, (cx, cy), radius, 255, -1)
            for a in range(-60, 90, 30):
                pt1 = (
                    int(cx + radius * math.cos(math.radians(a + 90))),
                    int(cy + radius * math.sin(math.radians(a + 90)) * 1.3),
                )
                pt2 = (
                    int(cx + radius * math.cos(math.radians(a - 90))),
                    int(cy + radius * math.sin(math.radians(a - 90)) * 1.3),
                )
                cv2.line(sprite, pt1, pt2, (*ftype["stripe"], 255),
                         max(3, radius // 6), cv2.LINE_AA)
            sprite[:, :, :3] = cv2.bitwise_and(sprite[:, :, :3], sprite[:, :, :3], mask=mask)

        hl_overlay = sprite.copy()
        cv2.ellipse(
            hl_overlay,
            (cx - radius // 3, cy - radius // 3),
            (radius // 3, radius // 4),
            -30, 0, 360,
            (*ftype["highlight"], 255), -1, cv2.LINE_AA
        )
        sprite[:, :, :3] = cv2.addWeighted(sprite[:, :, :3], 0.6, hl_overlay[:, :, :3], 0.4, 0)

        mask = np.zeros((size, size), dtype=np.uint8)
        cv2.circle(mask, (cx, cy), radius, 255, -1, cv2.LINE_AA)
        mask = cv2.GaussianBlur(mask, (5, 5), 0)
        sprite[:, :, 3] = mask

        stem_top = (cx, cy - radius - pad // 2)
        stem_bot = (cx, cy - radius + 2)
        cv2.line(sprite, stem_top, stem_bot, (*ftype["stem"], 255),
                 max(2, radius // 10), cv2.LINE_AA)

        leaf_center = (cx + radius // 4, cy - radius - pad // 3)
        cv2.ellipse(
            sprite, leaf_center, (radius // 4, radius // 7),
            30, 0, 360, (*ftype["leaf"], 255), -1, cv2.LINE_AA
        )

        return sprite

    def _get_fruit_sprite(self, ftype, radius):
        key = (ftype["name"], radius)
        if key not in self._fruit_sprites:
            self._fruit_sprites[key] = self._build_fruit_sprite(ftype, radius)
        return self._fruit_sprites[key]

    def draw_fruits(self, frame, fruits):
        for f in fruits:
            sprite = self._get_fruit_sprite(f.type, f.radius)
            self._blit_rgba(frame, sprite, int(f.x), int(f.y), f.angle)

    # ---------------- SLICED FRUIT HALVES ----------------

    def make_fruit_halves(self, ftype, radius, current_angle, slice_angle_deg):
        """
        Cuts the fruit's existing sprite into two RGBA halves along the
        actual swipe direction (slice_angle_deg), so the cut lines up
        with how you swiped, not a fixed direction.
        """
        base = self._get_fruit_sprite(ftype, radius)
        h, w = base.shape[:2]

        m = cv2.getRotationMatrix2D((w / 2, h / 2), current_angle, 1.0)
        rotated = cv2.warpAffine(
            base, m, (w, h), flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0)
        )

        half_mask = np.zeros((h, w), dtype=np.uint8)
        half_mask[: h // 2, :] = 255
        m2 = cv2.getRotationMatrix2D((w / 2, h / 2), slice_angle_deg, 1.0)
        mask_a = cv2.warpAffine(half_mask, m2, (w, h))
        mask_b = 255 - mask_a

        half_a = rotated.copy()
        half_a[:, :, 3] = cv2.bitwise_and(half_a[:, :, 3], mask_a)

        half_b = rotated.copy()
        half_b[:, :, 3] = cv2.bitwise_and(half_b[:, :, 3], mask_b)

        return half_a, half_b

    def draw_fruit_halves(self, frame, halves):
        for half in halves:
            sprite = half.sprite
            if half.alpha < 1.0:
                sprite = sprite.copy()
                sprite[:, :, 3] = (sprite[:, :, 3].astype(np.float32) * half.alpha).astype(np.uint8)
            self._blit_rgba(frame, sprite, int(half.x), int(half.y), half.angle)

    # ---------------- BOMBS ----------------

    def _build_bomb_sprite(self, radius=32):
        cache_key = "_bomb"
        if cache_key in self._fruit_sprites:
            return self._fruit_sprites[cache_key]

        pad = int(radius * 0.8) + 10
        size = radius * 2 + pad * 2
        cx, cy = size // 2, size // 2

        sprite = np.zeros((size, size, 4), dtype=np.uint8)

        for r in range(radius, 0, -1):
            f = r / radius
            shade = int(12 + 65 * (1 - f))
            ox = int(-radius * 0.2 * (1 - f))
            oy = int(-radius * 0.2 * (1 - f))
            cv2.circle(sprite, (cx + ox, cy + oy), r, (shade, shade, shade, 255), -1, cv2.LINE_AA)

        cv2.ellipse(sprite, (cx - radius // 3, cy - radius // 3),
                    (radius // 4, radius // 5), -30, 0, 360, (90, 90, 90, 255), -1, cv2.LINE_AA)

        mask = np.zeros((size, size), dtype=np.uint8)
        cv2.circle(mask, (cx, cy), radius, 255, -1, cv2.LINE_AA)
        mask = cv2.GaussianBlur(mask, (5, 5), 0)
        sprite[:, :, 3] = mask

        fuse_top = (cx + radius // 3, cy - radius - pad // 2)
        fuse_base = (cx + radius // 6, cy - radius + 2)
        cv2.line(sprite, fuse_base, fuse_top, (40, 70, 95, 255), max(2, radius // 10), cv2.LINE_AA)

        self._fruit_sprites[cache_key] = (sprite, fuse_top)
        return self._fruit_sprites[cache_key]

    def draw_bombs(self, frame, bombs):
        sprite, fuse_pt = self._build_bomb_sprite(32)
        h, w = sprite.shape[:2]

        for b in bombs:
            self._blit_rgba(frame, sprite, int(b.x), int(b.y), 0)

            sx = int(b.x - w // 2 + fuse_pt[0])
            sy = int(b.y - h // 2 + fuse_pt[1])
            flick = random.choice([(0, 255, 255), (0, 140, 255), (255, 255, 255)])
            r = random.randint(3, 6)
            cv2.circle(frame, (sx, sy), r, flick, -1, cv2.LINE_AA)

    # ---------------- BLITTING ----------------

    def _blit_rgba(self, frame, sprite, cx, cy, angle=0):
        if angle:
            h, w = sprite.shape[:2]
            m = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
            sprite = cv2.warpAffine(
                sprite, m, (w, h),
                flags=cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_CONSTANT,
                borderValue=(0, 0, 0, 0)
            )

        h, w = sprite.shape[:2]
        x1, y1 = cx - w // 2, cy - h // 2
        x2, y2 = x1 + w, y1 + h

        fx1, fy1 = max(x1, 0), max(y1, 0)
        fx2, fy2 = min(x2, frame.shape[1]), min(y2, frame.shape[0])
        if fx1 >= fx2 or fy1 >= fy2:
            return

        ix1, iy1 = fx1 - x1, fy1 - y1
        ix2, iy2 = ix1 + (fx2 - fx1), iy1 + (fy2 - fy1)

        roi = frame[fy1:fy2, fx1:fx2].astype(np.float32)
        crop = sprite[iy1:iy2, ix1:ix2].astype(np.float32)

        alpha = crop[:, :, 3:4] / 255.0
        blended = roi * (1 - alpha) + crop[:, :, :3] * alpha
        frame[fy1:fy2, fx1:fx2] = blended.astype(np.uint8)

    # ---------------- PARTICLES (juice splash) ----------------

    def draw_particles(self, frame, particles):
        for p in particles:
            if p.life <= 0:
                continue
            alpha = max(0.0, min(1.0, p.life / 20))
            radius = max(1, int(3 * alpha) + 1)
            cv2.circle(frame, (int(p.x), int(p.y)), radius, p.color, -1, cv2.LINE_AA)

    # ---------------- GAME OVER ----------------

    def draw_game_over(self, frame, score):
        h, w = frame.shape[:2]
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.55, frame, 0.45, 0, frame)

        text = "GAME OVER"
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.8, 4)
        cv2.putText(frame, text, ((w - tw) // 2, h // 2 - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 0, 255), 4, cv2.LINE_AA)

        score_text = f"Score: {score}"
        (sw, sh), _ = cv2.getTextSize(score_text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
        cv2.putText(frame, score_text, ((w - sw) // 2, h // 2 + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2, cv2.LINE_AA)

        hint = "Press R to restart, ESC to quit"
        (hw, hh), _ = cv2.getTextSize(hint, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        cv2.putText(frame, hint, ((w - hw) // 2, h // 2 + 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2, cv2.LINE_AA)