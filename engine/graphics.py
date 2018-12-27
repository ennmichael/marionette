from __future__ import annotations

from typing import Optional, List, Iterable, Any, Dict

from PIL import Image

from engine.physics import World
from engine.sdl import Texture, Renderer, Flip, Color
from engine.timer import Timer
from engine.utils import Rectangle, Direction


class Camera:
    __slots__ = 'view', 'window_dimensions', 'renderer'

    def __init__(self, view: Rectangle, window_dimensions: complex, renderer: Renderer) -> None:
        self.view = view
        self.window_dimensions = window_dimensions
        self.renderer = renderer

    def update(self) -> None:
        pass

    def render_texture(
            self, texture: Texture,
            source: Rectangle, destination: Rectangle,
            flip: Optional[Flip] = None) -> None:
        destination = self.scale_destination(destination)
        if (destination.right_real <= self.view.left_real or
                destination.left_real >= self.view.right_real or
                destination.lower_imag <= self.view.upper_imag or
                destination.upper_imag >= self.view.lower_imag):
            return
        self.renderer.render_texture(texture, source, destination, flip)

    def scale_destination(self, destination_rectangle: Rectangle) -> Rectangle:
        return Rectangle(
            upper_left=self.scale_coordinates(destination_rectangle.upper_left - self.view.upper_left),
            dimensions=self.scale_coordinates(destination_rectangle.dimensions))

    def scale_coordinates(self, coordinates: complex):
        return ((coordinates.real * self.window_dimensions.real) / self.view.dimensions.real +
                (coordinates.imag * self.window_dimensions.imag) / self.view.dimensions.imag * 1j)


class Animator:
    __slots__ = 'timer', 'sprites', 'current_sprite', 'flip'

    def __init__(self, timer: Timer, sprites: Dict[str, Sprite], current_sprite: str, loop: bool) -> None:
        assert current_sprite in sprites

        self.timer = timer
        self.sprites = sprites
        self.current_sprite = sprites[current_sprite]
        self.switch_sprite(current_sprite, loop)
        self.flip = Flip.NONE

    def switch_sprite(self, new_sprite: str, loop: bool) -> None:
        assert new_sprite in self.sprites

        self.current_sprite = self.sprites[new_sprite]
        self.current_sprite.animation.reset()
        if loop:
            self.current_sprite.animation.loop(self.timer)
        else:
            self.current_sprite.animation.play_once(self.timer)

    def render_current_sprite(self, camera: Camera, destination: Rectangle) -> None:
        self.current_sprite.render(camera, destination, self.flip)


class Sprite:
    __slots__ = 'texture', 'shells', 'animation'

    # FIXME This method is barnacles, it'll be useless when I start using a sprite atlas
    # There is a better way - load the Texture and PIL.Image right away and then pass them to some Sprite static method
    @staticmethod
    def load(renderer: Renderer, path: bytes, animation: Animation) -> Sprite:
        texture = Texture(renderer, path)
        image = Image.open(path)
        shells = list(find_shells(get_pixels(image), animation))
        return Sprite(texture, shells, animation)

    def __init__(self, texture: Texture, shells: List[Shell], animation: Animation) -> None:
        self.texture = texture
        self.shells = shells
        self.animation = animation

    def render(self, camera: Camera, destination: Rectangle, flip: Optional[Flip] = None) -> None:
        camera.render_texture(
            self.texture,
            source=self.animation.active_frame, destination=destination, flip=flip)


class Animation:
    __slots__ = 'starting_frame', 'frame_count', 'frame_delay', 'current_frame_num'

    def __init__(self, starting_frame: Rectangle, frame_count: int, frame_delay: int) -> None:
        self.starting_frame = starting_frame
        self.frame_count = frame_count
        self.frame_delay = frame_delay
        self.current_frame_num = 0

    def play_once(self, timer: Timer) -> None:
        def callback() -> None:
            if self.is_done:
                return
            self.advance()
            timer.add_task(callback, self.frame_delay, repeat=False)

        timer.add_task(callback, self.frame_delay, repeat=False)

    def loop(self, timer: Timer) -> None:
        def callback() -> None:
            self.advance()
            if self.is_done:
                self.reset()

        timer.add_task(callback, self.frame_delay, repeat=True)

    def advance(self) -> None:
        self.current_frame_num += 1
        if self.is_done:
            self.done()

    @property
    def is_done(self) -> bool:
        return self.current_frame_num >= self.frame_count

    def done(self) -> None:
        pass

    def reset(self) -> None:
        self.current_frame_num = 0

    @property
    def active_frame(self) -> Rectangle:
        return Rectangle(
            upper_left=(self.starting_frame.upper_left.real +
                        self.starting_frame.dimensions.real * self.current_frame_num +
                        self.starting_frame.upper_left.imag * 1j),
            dimensions=self.starting_frame.dimensions)


Pixels = List[List[Color]]

Silhouette = List[List[bool]]


def find_shells(pixels: Pixels, animation: Animation) -> Iterable[Shell]:
    yield from (
        Shell(silhouette=Shell.find_silhouette(frame_pixels), outline=list(Shell.find_outline(frame_pixels)))
        for frame_pixels in Shell.frames(pixels, animation))


class Shell:
    __slots__ = 'silhouette', 'outline'

    def __init__(self, silhouette: Silhouette, outline: List[complex]) -> None:
        self.silhouette = silhouette
        self.outline = outline

    @staticmethod
    def frames(pixels: Pixels, animation: Animation) -> Iterable[Pixels]:
        while not animation.is_done:
            frame = animation.active_frame
            yield [
                row[int(frame.left_real):int(frame.right_real)]
                for row in pixels[int(frame.upper_imag):int(frame.lower_imag)]
            ]
            animation.advance()
        animation.reset()

    @staticmethod
    def find_silhouette(pixels: Pixels) -> Silhouette:
        silhouette: Silhouette = []
        for row in pixels:
            silhouette.append([])
            for color in row:
                silhouette[-1].append(bool(color.a))
        return silhouette

    @staticmethod
    def find_outline(pixels: Pixels) -> Iterable[complex]:
        starting_position = Shell.outline_starting_position(pixels)
        position = starting_position
        direction = Direction.UPPER_RIGHT
        yield position
        while True:
            new_position = position + direction.coordinates
            if new_position == starting_position:
                return
            y = int(new_position.imag)
            x = int(new_position.real)
            if 0 <= y < len(pixels) and 0 <= x < len(pixels[0]) and pixels[y][x].a != 0:
                yield new_position
                position = new_position
                direction = Shell.next_outline_direction(direction)
            else:
                direction = direction.next_clockwise

    @staticmethod
    def outline_starting_position(pixels: Pixels) -> complex:
        for y, row in enumerate(pixels):
            for x, color in enumerate(row):
                if color.a != 0:
                    return x + y * 1j
        assert False

    @staticmethod
    def next_outline_direction(direction: Direction) -> Direction:
        if direction % 2 == 0:
            return Direction.from_int(direction + 1)
        return Direction.from_int(direction + 2)


class LightSource:
    __slots__ = 'position', 'intensity'

    def __init__(self, position: complex, intensity: float) -> None:
        self.position = position
        self.intensity = intensity

    def update(self) -> None:
        pass


class Lighting:
    __slots__ = 'light_sources', 'sprites'

    def __init__(self, light_sources: List[LightSource], sprites: List[Sprite]) -> None:
        self.light_sources = light_sources
        self.sprites = sprites

    def render_shadows(self, camera: Camera, world: World) -> None:
        pass


def get_pixels(image: Any) -> Pixels:
    pixels: Pixels = []
    for index, color in enumerate(image.getdata()):
        if index % image.size[0] == 0:
            pixels.append([])
        pixels[-1].append(Color(*color))
    return pixels
