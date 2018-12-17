#!/usr/bin/env python3

from engine.sdl import Window, Keyboard, quit_requested, Scancode, Color
from engine.physics import World, Entity, TerrainBox
from engine.timer import Timer


class TestEntity(Entity):
    def __init__(self) -> None:
        super().__init__(position=200 + 200j, dimensions=32 + 32j, mass=0.1)
        self.keyboard = Keyboard()
        self.max_velocity = 0.5
        self.speed = 0.1

    def update(self) -> None:
        if self.velocity.real > self.max_velocity:
            return

        if self.keyboard.key_down(Scancode.LEFT):
            self.apply_force(-self.speed)
        elif self.keyboard.key_down(Scancode.RIGHT):
            self.apply_force(self.speed)


if __name__ == '__main__':
    window = Window(b'Bourbank', dimensions=400 + 400j)
    e = TestEntity()
    ground = TerrainBox(position=20 + 360j, dimensions=360 + 20j)
    renderer = window.renderer()
    timer = Timer()
    world = World(timer, time_delta=20, gravity=0.6, drag=0.5, entities=[e, ground])

    while not quit_requested():
        renderer.render_clear()
        timer.update()
        renderer.set_draw_color(Color.black())
        renderer.fill_rectangle(e.checkbox())
        renderer.fill_rectangle(ground.checkbox())
        renderer.set_draw_color(Color.white())
        renderer.render_present()
