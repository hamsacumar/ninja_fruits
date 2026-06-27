import cv2
import mediapipe as mp

class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils

    def process(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return self.hands.process(rgb)

    def get_index_finger(self, results, frame_shape):
        if not results.multi_hand_landmarks:
            return None

        hand = results.multi_hand_landmarks[0]
        h, w, _ = frame_shape

        x = int(hand.landmark[8].x * w)
        y = int(hand.landmark[8].y * h)

        return (x, y)