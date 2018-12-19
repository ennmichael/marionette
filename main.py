#!/usr/bin/env python3

from engine.sdl import Window, Keyboard, Scancode, Color, Renderer, quit_requested
from engine.physics import World, Entity, TerrainBox
from engine.timer import Timer
from engine.utils import Line

FPS = 60


class TestEntity(Entity):
    def __init__(self, position: complex, dimensions: complex) -> None:
        super().__init__(position, dimensions, mass=0.5)
        self.keyboard = Keyboard()
        self.max_velocity = 60
        self.speed = 20
        self.jump_force = 5

    def update(self) -> None:
        if self.keyboard.key_down(Scancode.Y) or self.keyboard.key_down(Scancode.Z):
            self.apply_force(-self.jump_force * 1j)

        if abs(self.velocity.real) > self.max_velocity:
            return

        if self.keyboard.key_down(Scancode.LEFT):
            self.apply_force(-self.speed)
        elif self.keyboard.key_down(Scancode.RIGHT):
            self.apply_force(self.speed)


VISUAL_VELOCITY_MULTIPLIER = 5


def debug_draw(renderer: Renderer, world: World) -> None:
    for entity in world.entities:
        renderer.set_draw_color(Color.blue(10))
        renderer.fill_rectangle(entity.checkbox)
        renderer.set_draw_color(Color.red(150))
        renderer.draw_line(Line(entity.checkbox.center, entity.velocity * VISUAL_VELOCITY_MULTIPLIER))
        renderer.draw_line(Line(entity.checkbox.center - 1, entity.velocity * VISUAL_VELOCITY_MULTIPLIER))
        renderer.draw_line(Line(entity.checkbox.center + 1, entity.velocity * VISUAL_VELOCITY_MULTIPLIER))
        renderer.draw_line(Line(entity.checkbox.center - 1j, entity.velocity * VISUAL_VELOCITY_MULTIPLIER))
        renderer.draw_line(Line(entity.checkbox.center + 1j, entity.velocity * VISUAL_VELOCITY_MULTIPLIER))


def main() -> None:
    window = Window(b'Bourbank', dimensions=400 + 400j)
    e = TestEntity(position=200 + 100j, dimensions=32 + 32j)
    terrain = [
        TerrainBox(position=20 + 360j, dimensions=360 + 20j),
        TerrainBox(position=20 + 200j, dimensions=60 + 200j),
        TerrainBox(position=350 + 200j, dimensions=60 + 200j),
    ]
    renderer = window.renderer()
    world = World(timestep=10, gravity=2, horizontal_drag=0.2, entities=[e, *terrain])
    timer = Timer()

    # This is only for testing purposes
    def frame_advance() -> None:
        renderer.render_clear()
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
