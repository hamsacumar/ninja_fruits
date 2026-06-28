class GameLoop:
    def __init__(self, update, render):
        self.update = update
        self.render = render

    def run(self):
        while True:
            self.update()
            self.render()