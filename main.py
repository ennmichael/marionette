#!/usr/bin/env python3
from typing import Iterator

from engine import sdl
from engine.game import Game
from engine.graphics import Camera, FollowerCamera
from engine.physics import World, TerrainBox
from engine.sdl import Window, Color, destroying
from engine.timer import Time
from engine.utils import Line, Rectangle
from mario import Mario

FPS = 60

VISUAL_VELOCITY_MULTIPLIER = 0.1


# TODO Check every place where get_current_time gets called and make the flow of time linear, have it called only once per frame
# TODO Fix the background. Source and destination should be the same, both the having upper left corner at 0 and image size
# TODO Have an option for the camera to be limited. Currently corners are handled awkwardly.
# TODO Change the background color to something decent
# TODO As an exercise to the system make it so that when Mario falls from a very high place he is stunned and forced to be ducked for a little while.


ACTOR_DIMENSIONS = 16 + 32j


class MarioGame(Game):
    def __init__(self, debug: bool = False) -> None:
        super().__init__(fps=60)
        self.window = Window(b'', dimensions=400 + 400j)
        self.renderer = self.window.renderer()
        self.mario_texture = self.renderer.load_texture(b'res/mario.png')
        self.background_texture = self.renderer.load_texture(b'res/background.png')
        self.mario = Mario(keyboard=self.keyboard, upper_left=100 + 100j, texture=self.mario_texture)
        self.camera = FollowerCamera(
            target=self.mario, view_dimensions=400 + 400j,
            window_dimensions=400 + 400j, renderer=self.renderer)
        self.world = World(
            timestep=10, gravity=300, horizontal_drag=0.2,
            entities=[self.mario, *MarioGame.create_terrain()])

        self.debug = debug

    def destroy(self) -> None:
        self.background_texture.destroy()
        self.mario_texture.destroy()
        self.renderer.destroy()
        self.window.destroy()

    @staticmethod
    def create_terrain() -> Iterator[TerrainBox]:
        yield TerrainBox(Rectangle(upper_left=0 + 200j, dimensions=256 + 24j))
        yield TerrainBox(Rectangle(upper_left=288 + 184j, dimensions=64 + 40j))
        yield TerrainBox(Rectangle(upper_left=416 + 72j, dimensions=80 + 16j))
        yield TerrainBox(Rectangle(upper_left=432 + 48j, dimensions=48 + 48j))
        yield TerrainBox(Rectangle(upper_left=384 + 136j, dimensions=128 + 40j))
        yield TerrainBox(Rectangle(upper_left=400 + 176j, dimensions=96 + 48j))

    def frame_advance(self, time: Time) -> None:
        super().frame_advance(time)
        self.world.update(time)
        self.camera.update()
        self.redraw_frame()

    def redraw_frame(self) -> None:
        self.renderer.set_draw_color(Color.white())
        self.renderer.clear()
        self.mario.render(self.camera)
        if self.debug:
            self.debug_draw()
        self.renderer.present()

    def debug_draw(self) -> None:
        for entity in self.world.entities:
            self.camera.renderer.set_draw_color(Color.blue(a=80))
            self.camera.draw_rectangle(entity.checkbox, fill=True)
            self.camera.renderer.set_draw_color(Color.red(a=120))
            self.camera.draw_line(Line(entity.checkbox.center, entity.velocity * VISUAL_VELOCITY_MULTIPLIER))
            self.camera.draw_line(Line(entity.checkbox.center - 1, entity.velocity * VISUAL_VELOCITY_MULTIPLIER))
            self.camera.draw_line(Line(entity.checkbox.center + 1, entity.velocity * VISUAL_VELOCITY_MULTIPLIER))
            self.camera.draw_line(Line(entity.checkbox.center - 1j, entity.velocity * VISUAL_VELOCITY_MULTIPLIER))
            self.camera.draw_line(Line(entity.checkbox.center + 1j, entity.velocity * VISUAL_VELOCITY_MULTIPLIER))
            if entity.on_ground:
                self.camera.renderer.set_draw_color(Color.green(a=200))
                self.camera.draw_rectangle(Rectangle(entity.checkbox.upper_left, 3 + 3j), fill=True)


def main() -> None:
    with sdl.init_and_quit(), destroying(MarioGame(debug=True)) as game:
        game.main_loop()


if __name__ == '__main__':
    main()
