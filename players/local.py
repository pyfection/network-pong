

from kivy.core.window import Window


class Local:
    target = 0, 0

    def __init__(self):
        Window.bind(mouse_pos=lambda w, p: setattr(self, 'target', p))

    def update(self):
        return
