import cv2
from ai.hand_tracker import HandTracker

cap = cv2.VideoCapture(0)
tracker = HandTracker()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = tracker.process(frame)
    point = tracker.get_index_finger(results, frame.shape)

    if point:
        cv2.circle(frame, point, 10, (0,255,0), -1)

    cv2.imshow("AI Fruit Ninja - Hand Tracking", frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()