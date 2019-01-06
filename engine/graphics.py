from __future__ import annotations

from engine.physics import PhysicalEntity
from engine.sdl import Texture, Renderer, Flip, get_current_time
from engine.timer import Time
from engine.utils import Rectangle, Line


class Camera:
    __slots__ = 'view', 'window_dimensions', 'renderer'

    def __init__(self, view: Rectangle, window_dimensions: complex, renderer: Renderer) -> None:
        self.view = view
        self.window_dimensions = window_dimensions
        self.renderer = renderer

    def update(self) -> None:
        pass

    def draw_texture(
            self, texture: Texture, source: Rectangle, destination: Rectangle, flip: Flip = Flip.NONE) -> None:
        destination = scale_rectangle(self.view, destination, new_dimensions=self.window_dimensions)
        self.renderer.draw_texture(texture, source, destination, flip)

    def draw_rectangle(self, rectangle: Rectangle, fill: bool) -> None:
        self.renderer.draw_rectangle(
            scale_rectangle(self.view, rectangle, new_dimensions=self.window_dimensions), fill)

    def draw_line(self, line: Line) -> None:
        self.renderer.draw_line(scale_line(self.view, line, new_dimensions=self.window_dimensions))


def draw_background(background_texture: Texture, camera: Camera) -> None:
    source = Rectangle(upper_left=0, dimensions=camera.window_dimensions)
    destination = Rectangle(upper_left=0, dimensions=camera.window_dimensions)
    source.center = destination.center = camera.view.center
    camera.draw_texture(background_texture, source, destination)


def scale_rectangle(view: Rectangle, rectangle: Rectangle, new_dimensions: complex) -> Rectangle:
    return Rectangle(
        upper_left=scale_coordinates(view, rectangle.upper_left - view.upper_left, new_dimensions),
        dimensions=scale_coordinates(view, rectangle.dimensions, new_dimensions))


def scale_line(view: Rectangle, line: Line, new_dimensions: complex) -> Line:
    return Line(
        origin=scale_coordinates(view, line.origin - view.upper_left, new_dimensions),
        offset=scale_coordinates(view, line.offset, new_dimensions))


def scale_coordinates(view: Rectangle, coordinates: complex, new_dimensions: complex) -> complex:
    return ((coordinates.real * new_dimensions.real) / view.dimensions.real +
            (coordinates.imag * new_dimensions.imag) / view.dimensions.imag * 1j)


class FollowerCamera(Camera):
    __slots__ = 'target'

    def __init__(
            self, view_dimensions: complex, window_dimensions: complex,
            renderer: Renderer, target: PhysicalEntity) -> None:
        super().__init__(
            view=Rectangle(target.checkbox.upper_left, view_dimensions),
            window_dimensions=window_dimensions, renderer=renderer)
        self.target = target

    def update(self) -> None:
        self.view.center = self.target.checkbox.center


class SpritePlayer:
    __slots__ = 'sprite', 'advance_time'

    def __init__(self, sprite: Sprite) -> None:
        self.sprite = sprite
        self.advance_time = get_current_time() + self.sprite.animation.frame_delay
        # I don't like using get_current_time, but using a current_time parameter is so bad.
        # The parameter ends up leaking into so many other declarations and it just looks awkward.

    def update(self, time: Time) -> None:
        if self.is_done:
            return

        if time.current >= self.advance_time:
            self.sprite.animation.advance()
            self.advance_time += self.sprite.animation.frame_delay

    @property
    def is_done(self) -> bool:
        return self.sprite.animation.is_done


class Sprite:
    __slots__ = 'texture', 'animation', 'flip'

    def __init__(self, texture: Texture, animation: Animation) -> None:
        self.texture = texture
        self.animation = animation

    def render(self, camera: Camera, destination: Rectangle, flip: Flip = Flip.NONE) -> None:
        camera.draw_texture(self.texture, source=self.animation.active_frame, destination=destination, flip=flip)


class Animation:
    __slots__ = 'starting_frame', 'frame_count', 'frame_delay', 'current_frame_num', 'loop'

    def __init__(self, starting_frame: Rectangle, frame_count: int, frame_delay: int, loop: bool = False) -> None:
        self.starting_frame = starting_frame
        self.frame_count = frame_count
        self.frame_delay = frame_delay
        self.current_frame_num = 0
        self.loop = loop

    def advance(self) -> None:
        self.current_frame_num += 1
        if self.loop and self.is_done:
            self.reset()

    @property
    def is_done(self) -> bool:
        return self.current_frame_num >= self.frame_count

    def reset(self) -> None:
        self.current_frame_num = 0

    @property
    def active_frame(self) -> Rectangle:
        return Rectangle(
            upper_left=(self.starting_frame.upper_left.real +
                        self.starting_frame.dimensions.real * self.current_frame_num +
                        self.starting_frame.upper_left.imag * 1j),
            dimensions=self.starting_frame.dimensions)

# TODO Shadows
