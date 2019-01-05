#!/usr/bin/env python3

from engine import sdl
from engine.graphics import Camera, FollowerCamera
from engine.physics import World, TerrainBox
from engine.sdl import Window, Color, Keyboard, EventHandler, destroying
from engine.timer import Time
from engine.utils import Line, Rectangle
from mario import Mario

FPS = 60

VISUAL_VELOCITY_MULTIPLIER = 0.1


# TODO
# I might have fixed this, check it
# get_current_time should be called from one place and once place only
# world.update calls get_current_time
# sprite_player.update calls get_current_time


def debug_draw(camera: Camera, world: World) -> None:
    for entity in world.entities:
        camera.renderer.set_draw_color(Color.blue(a=80))
        camera.draw_rectangle(entity.checkbox, fill=True)
        camera.renderer.set_draw_color(Color.red(a=120))
        camera.draw_line(Line(entity.checkbox.center, entity.velocity * VISUAL_VELOCITY_MULTIPLIER))
        camera.draw_line(Line(entity.checkbox.center - 1, entity.velocity * VISUAL_VELOCITY_MULTIPLIER))
        camera.draw_line(Line(entity.checkbox.center + 1, entity.velocity * VISUAL_VELOCITY_MULTIPLIER))
        camera.draw_line(Line(entity.checkbox.center - 1j, entity.velocity * VISUAL_VELOCITY_MULTIPLIER))
        camera.draw_line(Line(entity.checkbox.center + 1j, entity.velocity * VISUAL_VELOCITY_MULTIPLIER))
        if entity.on_ground:
            camera.renderer.set_draw_color(Color.green(a=200))
            camera.draw_rectangle(Rectangle(entity.checkbox.upper_left, 3 + 3j), fill=True)


ACTOR_DIMENSIONS = 16 + 32j


def main() -> None:
    terrain = [
        TerrainBox(Rectangle(upper_left=20 + 360j, dimensions=360 + 20j)),
        # TerrainBox(Rectangle(upper_left=20 + 200j, dimensions=60 + 200j)),
        # TerrainBox(Rectangle(upper_left=100 + 350j, dimensions=140 + 100j)),
        # TerrainBox(Rectangle(upper_left=350 + 200j, dimensions=60 + 200j)),
    ]
    with sdl.init_and_quit(), \
            destroying(Window(b'', dimensions=400 + 400j)) as window, \
            destroying(window.renderer()) as renderer:
        time = Time.now()
        keyboard = Keyboard()
        event_handler = EventHandler(keyboard)

        mario = Mario(upper_left=100 + 100j, texture=renderer.load_texture(b'res/mario.png'))
        camera = FollowerCamera(
            target=mario, view_dimensions=400 + 400j,
            window_dimensions=400 + 400j, renderer=renderer)
        world = World(
            timestep=10, gravity=300, horizontal_drag=0.2,
            entities=[mario, *terrain])

        def redraw_frame() -> None:
            renderer.render_clear()
            mario.render(camera)
            debug_draw(camera, world)
            renderer.set_draw_color(Color.red(a=255))
            renderer.set_draw_color(Color.white())
            renderer.render_present()

        while not event_handler.quit_requested:
            # TODO Add framerate control
            time = time.updated()
            event_handler.update()
            world.update(time)
            camera.update()
            redraw_frame()


if __name__ == '__main__':
    main()
