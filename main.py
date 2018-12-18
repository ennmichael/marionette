#!/usr/bin/env python3

from engine.sdl import Window, Keyboard, Scancode, Color, quit_requested
from engine.physics import World, Entity, TerrainBox
from engine.timer import Timer


FPS = 60


class TestEntity(Entity):
    def __init__(self) -> None:
        super().__init__(position=200 + 200j, dimensions=32 + 32j, mass=0.5)
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


if __name__ == '__main__':
    window = Window(b'Bourbank', dimensions=400 + 400j)
    e = TestEntity()
    terrain = [
        TerrainBox(position=20 + 360j, dimensions=360 + 20j),
        TerrainBox(position=20 + 200j, dimensions=60 + 200j),
        TerrainBox(position=250 + 200j, dimensions=60 + 200j),
    ]
    renderer = window.renderer()
    world = World(timestep_milliseconds=10, gravity=2, horizontal_drag=0.2, entities=[e, *terrain])
    timer = Timer()

    # This is only for testing purposes
    def render_everything() -> None:
        renderer.render_clear()
        renderer.set_draw_color(Color.black())
        renderer.fill_rectangle(e.checkbox)
        e.update()
        for entity in terrain:
            renderer.fill_rectangle(entity.checkbox)
        renderer.set_draw_color(Color.white())
        renderer.render_present()

    timer.add_task(render_everything, delay=int(1000 / FPS), repeat=True)

    while not quit_requested():
        world.update()
        timer.update()
