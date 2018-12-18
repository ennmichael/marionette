from abc import ABC, abstractmethod

from engine.physics import Entity
from engine.sdl import Texture
from engine.utils import Rectangle
from engine.timer import Timer


class Camera:
    # TODO This class scales everything that gets rendered to the size of the screen
    # So, the size of the camera can be any value, and it will scale everything rendered so
    # that it takes up the full screen.
    pass


class Renderable(ABC):
    @abstractmethod
    def render(self, camera: Camera) -> None:
        pass


class Frame:
    __slots__ = 'start', 'dimensions', 'frame_count', 'current_frame_num'

    def __init__(self, start: complex, dimensions: complex, frame_count: int) -> None:
        self.start = start
        self.dimensions = dimensions
        self.frame_count = frame_count
        self.current_frame_num = 0

    def advance(self) -> None:
        self.current_frame_num += 1

    def done(self) -> bool:
        return self.current_frame_num >= self.frame_count

    def reset(self) -> None:
        self.current_frame_num = 0

    def rectangle(self) -> Rectangle:
        return Rectangle(
            upper_left=self.start + self.dimensions.real * self.current_frame_num + self.dimensions.imag * 1j,
            dimensions=self.dimensions)


class Sprite(Renderable):
    def __init__(self, timer: Timer, texture: Texture, entity: Entity, delay: int, frame: Frame) -> None:
        timer.add_task(self.timer_callback, delay, repeat=True)
        self.frame = frame
        self.texture = texture
        self.entity = entity

    def render_source(self) -> Rectangle:
        return self.frame.rectangle()

    def render_destination(self) -> Rectangle:
        return Rectangle(self.entity.position, self.entity.dimensions)

    def render(self, camera: Camera) -> None:
        pass

    def timer_callback(self) -> None:
        self.frame.advance()
