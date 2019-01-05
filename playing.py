from engine import sdl


if __name__ == '__main__':
    with sdl.init_and_quit(), sdl.destroying(sdl.Window(b'Title', 200 + 200j)) as window:
        keyboard = sdl.Keyboard()
        event_handler = sdl.EventHandler(keyboard)

        while not event_handler.quit_requested:
            event_handler.update()
            if keyboard.key_pressed(sdl.Scancode.SPACE):
                print('Pressed')
            if keyboard.key_released(sdl.Scancode.SPACE):
                print('Released')

