#!/usr/bin/env python3

from engine.sdl import Window, Dimensions, quit_requested


if __name__ == '__main__':
    window = Window(b'Bourbank', Dimensions(width=400, height=400))
    renderer = window.renderer()

    while not quit_requested():
        renderer.render_clear()
        renderer.render_present()
