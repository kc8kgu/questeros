"""Shared scene lifecycle."""


class Scene:
    show_stats = True

    def __init__(self, game):
        self.game = game

    def on_exit(self):
        pass

    def handle_event(self, event):
        return True

    def cancel_overlay(self):
        return False

    def update(self, dt):
        pass

    def draw(self):
        raise NotImplementedError
