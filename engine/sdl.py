from __future__ import annotations

import ctypes
import ctypes.util
import enum
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import NamedTuple, Any, List, Optional, Dict, TypeVar, Iterator, cast

from engine.utils import Rectangle, Line


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
    if not lib:
        raise RuntimeError(f'Library not found: {library_name}')
    return ctypes.CDLL(lib)


libsdl2 = load_library('sdl2')
libsdl2_image = load_library('sdl2_image')

libsdl2.SDL_GetError.restype = ctypes.c_char_p
libsdl2.SDL_GetKeyboardState.restype = ctypes.POINTER(ctypes.c_uint8)
libsdl2.SDL_CreateWindow.restype = ctypes.c_void_p
libsdl2.SDL_GetTicks.restype = ctypes.c_uint32

libsdl2.SDL_CreateRenderer.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_uint32]
libsdl2.SDL_CreateRenderer.restype = ctypes.c_void_p

libsdl2.SDL_SetRenderDrawColor.argtypes = [ctypes.c_void_p, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8]
libsdl2.SDL_RenderClear.argtypes = [ctypes.c_void_p]
libsdl2.SDL_RenderPresent.argtypes = [ctypes.c_void_p]
libsdl2.SDL_RenderFillRect.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
libsdl2.SDL_RenderDrawLine.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]


def quit_requested() -> bool:
    libsdl2.SDL_PumpEvents()
    return bool(libsdl2.SDL_PeepEvents(None, 0, EventAction.PEEK_EVENT, Event.QUIT, Event.QUIT))


class Error(Exception):
    def __init__(self) -> None:
        super().__init__(libsdl2.SDL_GetError())


class Color(NamedTuple):
    r: int
    g: int
    b: int
    a: int = 255

    @staticmethod
    def red(a: int = 255) -> Color:
        return Color(255, 0, 0, a)

    @staticmethod
    def green(a: int = 255) -> Color:
        return Color(0, 255, 0, a)

    @staticmethod
    def blue(a: int = 255) -> Color:
        return Color(0, 0, 255, a)

    @staticmethod
    def black(a: int = 255) -> Color:
        return Color(0, 0, 0, a)

    @staticmethod
    def white(a: int = 255) -> Color:
        return Color(255, 255, 255, a)


def rectangle_sdl_parameter(rect: Rectangle) -> Any:
    class SdlRect(ctypes.Structure):
        _fields_ = [
            ('x', ctypes.c_int), ('y', ctypes.c_int),
            ('w', ctypes.c_int), ('h', ctypes.c_int)
        ]

    return SdlRect(
        int(rect.upper_left.real), int(rect.upper_left.imag),
        int(rect.dimensions.real), int(rect.dimensions.imag))


def get_current_time() -> int:
    return cast(int, libsdl2.SDL_GetTicks())


class Destroyable(ABC):
    @abstractmethod
    def destroy(self) -> None:
        pass


class Window(Destroyable):
    __slots__ = 'sdl_window'

    def __init__(self, title: bytes, dimensions: complex) -> None:
        x = int(dimensions.real / 2)
        y = int(dimensions.imag / 2)
        self.sdl_window = libsdl2.SDL_CreateWindow(title, x, y, int(dimensions.real), int(dimensions.imag), 0)
        if not self.sdl_window:
            raise Error

    def destroy(self) -> None:
        libsdl2.SDL_DestroyWindow(self.sdl_window)

    def renderer(self, draw_color: Optional[Color] = None) -> Renderer:
        return Renderer(self, draw_color)


class Texture(Destroyable):
    __slots__ = 'sdl_texture'

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
    def dimensions(self) -> complex:
        return complex(self.width, self.height)

    def destroy(self) -> None:
        libsdl2.SDL_DestroyTexture(self.sdl_texture)


LoadedTextures = Dict[bytes, Texture]


class Renderer(Destroyable):
    __slots__ = 'sdl_renderer'

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

    def fill_rectangle(self, rectangle: Rectangle) -> None:
        if libsdl2.SDL_RenderFillRect(self.sdl_renderer, ctypes.byref(rectangle_sdl_parameter(rectangle))) < 0:
            raise Error

    def draw_line(self, line: Line) -> None:
        if libsdl2.SDL_RenderDrawLine(
                self.sdl_renderer, int(line.start.real), int(line.start.imag),
                int(line.end.real), int(line.end.imag)) < 0:
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
                self.sdl_renderer, texture.sdl_texture, ctypes.byref(rectangle_sdl_parameter(src)),
                ctypes.byref(rectangle_sdl_parameter(dst)), ctypes.c_double(0), None, flip or Flip.NONE) < 0:
            raise Error


DestroyableT = TypeVar('DestroyableT', bound=Destroyable)


@contextmanager
def destroying(resource: DestroyableT) -> Iterator[DestroyableT]:
    try:
        yield resource
    finally:
        if isinstance(resource, list):
            for r in resource:
                r.destroy()
        else:
            resource.destroy()


class Keyboard:
    __slots__ = 'keyboard_ptr'

    def __init__(self) -> None:
        self.keyboard_ptr = libsdl2.SDL_GetKeyboardState(None)

    def key_down(self, scancode: Scancode) -> bool:
        return bool(self.keyboard_ptr[scancode])
