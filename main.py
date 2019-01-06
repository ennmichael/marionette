#!/usr/bin/env python3
from typing import Iterator

from engine import sdl
from engine.game import Game
from engine.graphics import FollowerCamera
from engine.physics import World, TerrainBox
from engine.sdl import Window, Color, destroying, Texture
from engine.timer import Time
from engine.utils import Line, Rectangle
from mario import Mario

FPS = 60

VISUAL_VELOCITY_MULTIPLIER = 0.1

# TODO Fix collision checking
# TODO As an exercise to the system make it so that when Mario falls from a very high place he is stunned and forced to be ducked for a little while.
# TODO FPS isn't precise, maybe use floats instead of ints, i.e. use seconds instead of milliseconds?


ACTOR_DIMENSIONS = 16 + 32j


class Background:
    def __init__(self, color: Color, texture: Texture) -> None:
        self.color = color
        self.texture = texture


class MarioGame(Game):
    def __init__(self, debug: bool = False) -> None:
        super().__init__(fps=60)
        self.window = Window(b'', dimensions=400 + 400j)
        self.renderer = self.window.renderer()
        self.mario_texture = self.renderer.load_texture(b'res/mario.png')
        self.background = Background(
            color=Color(107, 142, 255), texture=self.renderer.load_texture(b'res/background.png'))
        self.mario = Mario(keyboard=self.keyboard, upper_left=100 + 100j, texture=self.mario_texture)
        self.camera = FollowerCamera(
            target=self.mario, view_dimensions=400 + 400j,
            window_dimensions=400 + 400j, renderer=self.renderer)
        self.world = World(
            timestep=2, gravity=300, horizontal_drag=0.2,
            entities=[self.mario, *MarioGame.create_terrain()])

        self.debug = debug

    def destroy(self) -> None:
        self.background.texture.destroy()
        self.mario_texture.destroy()
        self.renderer.destroy()
        self.window.destroy()

    @staticmethod
    def create_terrain() -> Iterator[TerrainBox]:
        yield TerrainBox(Rectangle(upper_left=0 + 200j, dimensions=256 + 24j))
        yield TerrainBox(Rectangle(upper_left=288 + 184j, dimensions=64 + 16j))
        yield TerrainBox(Rectangle(upper_left=416 + 72j, dimensions=80 + 16j))
        yield TerrainBox(Rectangle(upper_left=384 + 136j, dimensions=128 + 40j))
        yield TerrainBox(Rectangle(upper_left=512 + 184j, dimensions=48 + 16j))
        yield TerrainBox(Rectangle(upper_left=560 + 120j, dimensions=80 + 16j))
        yield TerrainBox(Rectangle(upper_left=640 + 56j, dimensions=112 + 16j))

    def frame_advance(self, time: Time) -> None:
        super().frame_advance(time)
        self.world.update(time)
        self.camera.update()
        self.redraw_frame()

    def redraw_frame(self) -> None:
        self.draw_background()
        self.mario.render(self.camera)
        if self.debug:
            self.debug_draw()
        self.renderer.present()

    def draw_background(self) -> None:
        self.renderer.set_draw_color(self.background.color)
        self.renderer.clear()
        whole_background = Rectangle(upper_left=0, dimensions=self.background.texture.dimensions)
        self.camera.draw_texture(self.background.texture, source=whole_background, destination=whole_background)

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
    with sdl.init_and_quit(), destroying(MarioGame()) as game:
        game.main_loop()


if __name__ == '__main__':
    main()
