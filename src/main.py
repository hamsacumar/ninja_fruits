import cv2
import random
import math

from ai.hand_tracker import HandTracker
from ai.motion_predictor import MotionPredictor

from entities.blade import Blade
from entities.fruit_half import FruitHalf

from rendering.renderer import Renderer

from game.fruit_manager import FruitManager
from game.bomb_manager import BombManager
from game.collision_detector import CollisionDetector
from game.score_manager import ScoreManager
from game.particle_manager import ParticleManager
from game.splatter_manager import SplatterManager

from core.game_loop import GameLoop


# ---------------- INIT ----------------

cap = cv2.VideoCapture(0)

FRAME_W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 640
FRAME_H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 480

tracker = HandTracker()
predictor = MotionPredictor()

blade = Blade()
renderer = Renderer()

fruit_manager = FruitManager()
bomb_manager = BombManager()
detector = CollisionDetector()
score_manager = ScoreManager()

particle_manager = ParticleManager()
splatter = SplatterManager(FRAME_W, FRAME_H)

fruit_halves = []

frame = None
point = None
frame_count = 0
game_over = False


def reset_game():
    global frame_count, game_over
    fruit_manager.fruits.clear()
    bomb_manager.bombs.clear()
    fruit_halves.clear()
    particle_manager.particles.clear()
    splatter.clear()
    score_manager.reset()
    blade.clear()
    frame_count = 0
    game_over = False


# ---------------- UPDATE LOGIC ----------------

def update():
    global frame, point, frame_count, game_over

    ret, frame = cap.read()
    if not ret:
        return

    results = tracker.process(frame)
    point = tracker.get_index_finger(results, frame.shape)

    predictor.update(point)
    smoothed = predictor.smooth()
    predicted = predictor.predict_next()

    final_point = point if smoothed is None else smoothed

    if predicted and final_point:
        final_point = (
            int((final_point[0] + predicted[0]) / 2),
            int((final_point[1] + predicted[1]) / 2)
        )

    blade.update(final_point)

    # these keep animating even after game over (falling halves, fading splatter, etc.)
    for half in fruit_halves[:]:
        half.update()
        if half.life <= 0:
            fruit_halves.remove(half)

    particle_manager.update()
    splatter.update()

    if game_over:
        return

    fruit_manager.update()
    bomb_manager.update()

    frame_count += 1
    if frame_count % 60 == 0:
        if random.random() < 0.18:
            bomb_manager.spawn(frame.shape[1], frame.shape[0])
        else:
            fruit_manager.spawn(frame.shape[1], frame.shape[0])

    # ---- fruit collisions: slice into two real halves ----
    for fruit in fruit_manager.fruits[:]:
        hit, angle = detector.check_with_angle(fruit, blade.points)
        if not hit:
            continue

        fruit_manager.fruits.remove(fruit)

        if angle is None:
            angle = 0.0

        half_a, half_b = renderer.make_fruit_halves(fruit.type, fruit.radius, fruit.angle, angle)

        # halves separate perpendicular to the swipe direction
        rad = math.radians(angle + 90)
        push = 3.5
        sep_x = math.cos(rad) * push
        sep_y = math.sin(rad) * push

        fruit_halves.append(FruitHalf(fruit.x, fruit.y, half_a,
                                       fruit.vx - sep_x, fruit.vy - sep_y - 2,
                                       random.uniform(-6, 6)))
        fruit_halves.append(FruitHalf(fruit.x, fruit.y, half_b,
                                       fruit.vx + sep_x, fruit.vy + sep_y - 2,
                                       random.uniform(-6, 6)))

        particle_manager.emit(int(fruit.x), int(fruit.y), 18, fruit.type["juice"])
        splatter.splash(int(fruit.x), int(fruit.y), fruit.type["juice"])
        score_manager.add()

    # ---- bomb collisions: game over ----
    for bomb in bomb_manager.bombs[:]:
        if detector.check(bomb, blade.points):
            bomb_manager.bombs.remove(bomb)
            particle_manager.emit(int(bomb.x), int(bomb.y), 35, (40, 40, 40))
            splatter.splash(int(bomb.x), int(bomb.y), (20, 20, 20), blobs=10, spread=70)
            game_over = True


# ---------------- RENDER ----------------

def render():
    global frame, point

    if frame is None:
        return

    if point:
        cv2.circle(frame, point, 2, (192, 192, 192), -1)

    renderer.draw_blade(frame, blade)
    renderer.draw_fruits(frame, fruit_manager.fruits)
    renderer.draw_bombs(frame, bomb_manager.bombs)
    renderer.draw_fruit_halves(frame, fruit_halves)
    renderer.draw_particles(frame, particle_manager.particles)

    splatter.apply(frame)

    cv2.putText(
        frame,
        f"Score: {score_manager.score}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 255),
        2
    )

    if game_over:
        renderer.draw_game_over(frame, score_manager.score)

    cv2.imshow("AI Fruit Ninja", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC
        cap.release()
        cv2.destroyAllWindows()
        exit()
    elif key in (ord('r'), ord('R')) and game_over:
        reset_game()


# ---------------- GAME LOOP ----------------

game = GameLoop(update, render)
game.run()