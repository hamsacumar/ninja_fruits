class ScoreManager:
    def __init__(self):
        self.score = 0

    def add(self):
        self.score += 1

    def reset(self):
        self.score = 0