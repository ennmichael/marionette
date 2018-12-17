#!/usr/bin/env python3

from engine.sdl import Window, quit_requested


if __name__ == '__main__':
    window = Window(b'Bourbank', dimensions=400 + 400j)
    renderer = window.renderer()

    while not quit_requested():
        renderer.render_clear()
        renderer.render_present()
