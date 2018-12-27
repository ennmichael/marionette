#!/usr/bin/env python3

from engine.graphics import Animator, Sprite, Animation, Camera, FollowerCamera
from engine.physics import World, TerrainBox
from engine.sdl import Window, Keyboard, Scancode, Color, Renderer, quit_requested, destroying, Flip
from engine.timer import Timer
from engine.utils import Line, Rectangle
from game import Actor

FPS = 60


class TestActor(Actor):
    def __init__(self, animator: Animator, checkbox: Rectangle) -> None:
        super().__init__(animator, checkbox)
        self.keyboard = Keyboard()
        self.movement_speed = 200
        self.jump_velocity = -200j

    def update(self) -> None:
        if self.velocity.real < 0:
            self.animator.flip = Flip.HORIZONTAL
        elif self.velocity.real > 0:
            self.animator.flip = Flip.NONE

    def physics_update(self) -> None:
        self.update_jump()
        self.update_movement()

    def update_jump(self) -> None:
        if not self.on_ground or self.velocity.imag < 0:
            return

        if self.keyboard.key_down(Scancode.Y) or self.keyboard.key_down(Scancode.Z):
            self.velocity += self.jump_velocity

    def update_movement(self) -> None:
        if self.keyboard.key_down(Scancode.LEFT):
            self.velocity = -self.movement_speed + self.velocity.imag * 1j
        elif self.keyboard.key_down(Scancode.RIGHT):
            self.velocity = self.movement_speed + self.velocity.imag * 1j


VISUAL_VELOCITY_MULTIPLIER = 0.1


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
        # TerrainBox(Rectangle(upper_left=20 + 200j, dimensions=60 + 200j)),
        # TerrainBox(Rectangle(upper_left=100 + 350j, dimensions=140 + 100j)),
        # TerrainBox(Rectangle(upper_left=350 + 200j, dimensions=60 + 200j)),
    ]
    with destroying(Window(b'IGOR', dimensions=400 + 400j)) as window, destroying(window.renderer()) as renderer:
        timer = Timer()
        test_actor = create_test_actor(renderer, timer)
        camera = FollowerCamera(
            target=test_actor, view=Rectangle(upper_left=100 + 200j, dimensions=400 + 400j),
            window_dimensions=400 + 400j, renderer=renderer)
        world = World(
            timestep=10, gravity=300, horizontal_drag=0.2,
            entities=[test_actor, *terrain])

        # This is only for testing purposes
        def frame_advance() -> None:
            renderer.render_clear()
            test_actor.render(camera)
            debug_draw(camera, world)
            for entity in world.entities:
                entity.update()
            renderer.set_draw_color(Color.white())
            renderer.render_present()

        timer.add_task(frame_advance, delay=int(1000 / FPS), repeat=True)

        while not quit_requested():
            world.update()
            camera.update()
            timer.update()


if __name__ == '__main__':
    main()
