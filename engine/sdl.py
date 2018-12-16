from __future__ import annotations

import ctypes
import ctypes.util
import enum
from contextlib import contextmanager
from typing import NamedTuple, Any, List, Optional, Dict, TypeVar, Iterator


@enum.unique
class Event(enum.IntEnum):
    QUIT = 0x100


@enum.unique
class EventAction(enum.IntEnum):
    PEEK_EVENT = 1


@enum.unique
class Flip(enum.IntEnum):
    NONE = 0
    HORIZONTAL = 1
    VERTICAL = 2


@enum.unique
class Scancode(enum.IntEnum):
    X = 27
    Y = 28
    Z = 29
    RIGHT = 79
    LEFT = 80


def load_library(library_name: str) -> ctypes.CDLL:
    lib = ctypes.util.find_library(library_name)
    return ctypes.CDLL(lib)


libsdl2 = load_library('sdl2')
libsdl2_image = load_library('sdl2_image')

libsdl2.SDL_GetError.restype = ctypes.c_char_p
libsdl2.SDL_GetKeyboardState.restype = ctypes.POINTER(ctypes.c_uint8)
libsdl2.SDL_CreateWindow.restype = ctypes.c_void_p

libsdl2.SDL_CreateRenderer.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_uint32]
libsdl2.SDL_CreateRenderer.restype = ctypes.c_void_p

libsdl2.SDL_SetRenderDrawColor.argtypes = [ctypes.c_void_p, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8]
libsdl2.SDL_RenderClear.argtypes = [ctypes.c_void_p]
libsdl2.SDL_RenderPresent.argtypes = [ctypes.c_void_p]


def quit_requested() -> bool:
    libsdl2.SDL_PumpEvents()
    return bool(libsdl2.SDL_PeepEvents(None, 0, EventAction.PEEK_EVENT, Event.QUIT, Event.QUIT))


class Error(Exception):
    def __init__(self) -> None:
        super().__init__(libsdl2.SDL_GetError())


class Dimensions(NamedTuple):
    width: int
    height: int


class Color(NamedTuple):
    r: int
    g: int
    b: int
    a: int = 255

    @staticmethod
    def black() -> Color:
        return Color(0, 0, 0)

    @staticmethod
    def white() -> Color:
        return Color(255, 255, 255)


class Rectangle(NamedTuple):
    upper_left: complex
    dimensions: Dimensions

    def horizontally_overlaps(self, r: Rectangle) -> bool:
        return not (r.upper_right.real < self.upper_left.real
                    or r.upper_left.real > self.upper_right.real)

    def vertically_overlaps(self, r: Rectangle) -> bool:
        return not (r.lower_right.imag < self.upper_right.imag
                    or r.upper_right.imag > self.lower_right.imag)

    def is_above(self, r: Rectangle) -> bool:
        return self.lower_right.imag <= r.upper_right.imag

    def is_left_from(self, r: Rectangle) -> bool:
        return self.lower_right.real <= r.lower_left.real

    @property
    def upper_right(self) -> complex:
        return self.upper_left + self.width

    @property
    def lower_right(self) -> complex:
        return self.upper_right + self.height * 1j

    @property
    def lower_left(self) -> complex:
        return self.upper_left + self.height * 1j

    @property
    def width(self) -> int:
        return self.dimensions.width

    @property
    def height(self) -> int:
        return self.dimensions.height

    @property
    def as_sdl_parameter(self) -> Any:
        class SdlRect(ctypes.Structure):
            _fields_ = [
                ('x', ctypes.c_int), ('y', ctypes.c_int),
                ('w', ctypes.c_int), ('h', ctypes.c_int)
            ]

        return SdlRect(int(self.upper_left.real),
                       int(self.upper_left.imag),
                       self.width, self.height)


class Window:
    def __init__(self, title: bytes, dimensions: Dimensions) -> None:
        x = int(dimensions.width / 2)
        y = int(dimensions.height / 2)
        self.sdl_window = libsdl2.SDL_CreateWindow(title, x, y, dimensions.width, dimensions.height, 0)
        if not self.sdl_window:
            raise Error

    def destroy(self) -> None:
        libsdl2.SDL_DestroyWindow(self.sdl_window)

    def renderer(self, draw_color: Optional[Color] = None) -> Renderer:
        return Renderer(self, draw_color)


LoadedTextures = Dict[bytes, 'Texture']


class Renderer:
    def __init__(self, window: Window, draw_color: Optional[Color] = None) -> None:
        self.sdl_renderer = libsdl2.SDL_CreateRenderer(window.sdl_window, -1, 0)
        if not self.sdl_renderer:
            raise Error
        self.set_draw_color(draw_color or Color.white())

    def destroy(self) -> None:
        libsdl2.SDL_DestroyRenderer(self.sdl_renderer)

    def load_texture(self, path: bytes) -> Texture:
        return Texture(self, path)

    def load_textures(self, paths: List[bytes]) -> LoadedTextures:
        return {path: self.load_texture(path) for path in paths}

    def render_clear(self) -> None:
        if libsdl2.SDL_RenderClear(self.sdl_renderer) < 0:
            raise Error

    def render_present(self) -> None:
        if libsdl2.SDL_RenderPresent(self.sdl_renderer) < 0:
            raise Error

    def fill_rectangle(self, r: Rectangle) -> None:
        if libsdl2.SDL_RenderFillRect(self.sdl_renderer, ctypes.byref(r.as_sdl_parameter)) < 0:
            raise Error

    def draw_line(self, start: complex, end: complex) -> None:
        if libsdl2.SDL_RenderDrawLine(
                self.sdl_renderer, int(start.real), int(start.imag),
                int(end.real), int(end.imag)) < 0:
            raise Error

    def get_draw_color(self) -> Color:
        r = ctypes.c_int()
        g = ctypes.c_int()
        b = ctypes.c_int()
        a = ctypes.c_int()

        if libsdl2.SDL_GetRenderDrawColor(
                self.sdl_renderer,
                ctypes.byref(r), ctypes.byref(g), ctypes.byref(b), ctypes.byref(a)) < 0:
            raise Error

        return Color(r.value, g.value, b.value, a.value)

    def set_draw_color(self, color: Color) -> None:
        if libsdl2.SDL_SetRenderDrawColor(self.sdl_renderer, color.r, color.g, color.b, color.a) < 0:
            raise Error

    def render_texture(
            self, texture: Texture, src: Rectangle, dst: Rectangle,
            flip: Optional[Flip] = None) -> None:
        if libsdl2.SDL_RenderCopyEx(
                self.sdl_renderer, texture.sdl_texture, ctypes.byref(src.as_sdl_parameter),
                ctypes.byref(dst.as_sdl_parameter), ctypes.c_double(0), None, flip or Flip.NONE) < 0:
            raise Error


class Texture:
    def __init__(self, renderer: Renderer, path: bytes) -> None:
        self.sdl_texture = libsdl2_image.IMG_LoadTexture(renderer.sdl_renderer, path)
        if not self.sdl_texture:
            raise Error

    @property
    def height(self) -> int:
        h = ctypes.c_int(0)
        if libsdl2.SDL_QueryTexture(self.sdl_texture, None, None, None, ctypes.byref(h)) < 0:
            raise Error

        return h.value

    @property
    def width(self) -> int:
        w = ctypes.c_int(0)
        if libsdl2.SDL_QueryTexture(self.sdl_texture, None, None, ctypes.byref(w), None) < 0:
            raise Error

        return w.value

    @property
    def dimensions(self) -> Dimensions:
        return Dimensions(self.width, self.height)

    def destroy(self) -> None:
        libsdl2.SDL_DestroyTexture(self.sdl_texture)


Destroyable = TypeVar('Destroyable')


@contextmanager
def destroying(resource: Destroyable) -> Iterator[Destroyable]:
    try:
        yield resource
    finally:
        if isinstance(resource, list):
            for r in resource:
                r.destroy()
        else:
            resource.destroy()


class Keyboard:
    def __init__(self) -> None:
        self.keyboard_ptr = libsdl2.SDL_GetKeyboardState(None)

    def key_down(self, scancode: Scancode) -> bool:
        return bool(self.keyboard_ptr[scancode])
