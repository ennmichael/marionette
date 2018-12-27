#!/usr/bin/env python3
from typing import Optional

from engine.graphics import Animator, Sprite, Animation, Camera
from engine.physics import World, TerrainBox
from engine.sdl import Window, Keyboard, Scancode, Color, Renderer, quit_requested, destroying, Flip
from engine.timer import Timer
from engine.utils import Line, Rectangle
from game import Actor

FPS = 60


class TestActor(Actor):
    def __init__(self, animator: Animator, checkbox: Rectangle) -> None:
        super().__init__(animator, checkbox, mass=0.5)
        self.keyboard = Keyboard()
        self.max_velocity = 60
        self.speed = 20
        self.jump_force = -20j

    # This is where we kind of need state machines
    # And a lot of ugly nested classes, probably

    def update(self) -> None:
        self.update_jump()
        self.update_movement()
        if self.velocity.real < 0:
            self.animator.flip = Flip.HORIZONTAL
        elif self.velocity.real > 0:
            self.animator.flip = Flip.NONE
        else:
            pass

    def update_jump(self) -> None:
        if not self.on_ground or self.force.imag < 0:
            return

        if self.keyboard.key_down(Scancode.Y) or self.keyboard.key_down(Scancode.Z):
            self.apply_force(self.jump_force)

    def update_movement(self) -> None:
        if abs(self.velocity.real) > self.max_velocity:
            return

        if self.keyboard.key_down(Scancode.LEFT):
            self.apply_force(-self.speed)
        elif self.keyboard.key_down(Scancode.RIGHT):
            self.apply_force(self.speed)

    def render(self, camera: Camera) -> None:
        super().render(camera)
        print(self.animator.current_sprite.animation.current_frame_num)


VISUAL_VELOCITY_MULTIPLIER = 5


def debug_draw(renderer: Renderer, world: World) -> None:
    for entity in world.entities:
        renderer.set_draw_color(Color.blue(a=80))
        renderer.fill_rectangle(entity.checkbox)
        renderer.set_draw_color(Color.red(a=120))
        renderer.draw_line(Line(entity.checkbox.center, entity.velocity * VISUAL_VELOCITY_MULTIPLIER))
        renderer.draw_line(Line(entity.checkbox.center - 1, entity.velocity * VISUAL_VELOCITY_MULTIPLIER))
        renderer.draw_line(Line(entity.checkbox.center + 1, entity.velocity * VISUAL_VELOCITY_MULTIPLIER))
        renderer.draw_line(Line(entity.checkbox.center - 1j, entity.velocity * VISUAL_VELOCITY_MULTIPLIER))
        renderer.draw_line(Line(entity.checkbox.center + 1j, entity.velocity * VISUAL_VELOCITY_MULTIPLIER))
        if entity.on_ground:
            renderer.set_draw_color(Color.green(a=200))
            renderer.fill_rectangle(Rectangle(entity.position, 3 + 3j))


ACTOR_DIMENSIONS = 16 + 32j


def create_test_actor(renderer: Renderer, timer: Timer) -> TestActor:
    return TestActor(
        animator=Animator(
            timer,
            sprites={
                'running': Sprite.load(
                    renderer, path=b'res/mario.png',
                    animation=Animation(
                        starting_frame=Rectangle(upper_left=0, dimensions=ACTOR_DIMENSIONS),
                        frame_count=4, frame_delay=500))
            },
            current_sprite='running', loop=True),
        checkbox=Rectangle(upper_left=200 + 100j, dimensions=ACTOR_DIMENSIONS))


def main() -> None:
    terrain = [
        TerrainBox(Rectangle(upper_left=20 + 360j, dimensions=360 + 20j)),
        TerrainBox(Rectangle(upper_left=20 + 200j, dimensions=60 + 200j)),
        TerrainBox(Rectangle(upper_left=350 + 200j, dimensions=60 + 200j)),
    ]
    with destroying(Window(b'IGOR', dimensions=400 + 400j)) as window, destroying(window.renderer()) as renderer:

        camera = Camera(
            view=Rectangle(upper_left=0, dimensions=400 + 400j),
            window_dimensions=400 + 400j, renderer=renderer)

        timer = Timer()
        test_actor = create_test_actor(renderer, timer)
        world = World(
            timestep=10, gravity=2, horizontal_drag=0.2,
            entities=[test_actor, *terrain])

        # This is only for testing purposes
        def frame_advance() -> None:
            renderer.render_clear()
            test_actor.render(camera)
            debug_draw(renderer, world)
            for entity in world.entities:
                entity.update()
            renderer.set_draw_color(Color.white())
            renderer.render_present()

        timer.add_task(frame_advance, delay=int(1000 / FPS), repeat=True)

        while not quit_requested():
            world.update()
            timer.update()


if __name__ == '__main__':
    main()
