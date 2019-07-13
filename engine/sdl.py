from __future__ import annotations

import ctypes
import ctypes.util
import enum
import os
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import NamedTuple, List, Optional, Dict, TypeVar, Iterator, cast, DefaultDict

from engine.utils import Rectangle, Line


@enum.unique
class EventType(enum.IntEnum):
    QUIT = 0x100
    KEY_DOWN = 0x300
    KEY_UP = 0x301


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
    LEFT_CTRL = 224
    SPACE = 44


def load_library(library_name: str) -> ctypes.CDLL:
    os.environ['PATH'] = os.getcwd() + os.pathsep + os.environ['PATH']
    lib = ctypes.util.find_library(library_name)
    if not lib:
        raise RuntimeError(f'Library not found: {library_name}')
    return ctypes.CDLL(lib)


@contextmanager
def init_and_quit() -> Iterator[None]:
    init_subsystems()
    yield
    quit_subsystems()


libsdl2 = load_library('sdl2')
libsdl2_image = load_library('sdl2_image')


def init_subsystems() -> None:
    libsdl2.SDL_GetError.restype = ctypes.c_char_p
    libsdl2.SDL_CreateWindow.restype = ctypes.c_void_p
    libsdl2.SDL_GetTicks.restype = ctypes.c_uint32
    libsdl2.SDL_PollEvent.restype = ctypes.POINTER(RawEvent)

    libsdl2.SDL_CreateRenderer.argtypes = ctypes.c_void_p, ctypes.c_int, ctypes.c_uint32
    libsdl2.SDL_CreateRenderer.restype = ctypes.c_void_p

    libsdl2.SDL_SetRenderDrawColor.argtypes = (
        ctypes.c_void_p, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8)
    libsdl2.SDL_SetRenderDrawBlendMode.argtypes = ctypes.c_void_p, ctypes.c_int
    libsdl2.SDL_RenderClear.argtypes = (ctypes.c_void_p,)
    libsdl2.SDL_RenderPresent.argtypes = (ctypes.c_void_p,)
    libsdl2.SDL_RenderFillRect.argtypes = ctypes.c_void_p, ctypes.c_void_p
    libsdl2.SDL_RenderDrawLine.argtypes = ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int
    libsdl2.SDL_RenderCopyEx.argtypes = (
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
        ctypes.c_double, ctypes.c_void_p, ctypes.c_int)
    libsdl2.SDL_DestroyWindow.argtypes = (ctypes.c_void_p,)
    libsdl2.SDL_DestroyRenderer.argtypes = (ctypes.c_void_p,)
    libsdl2.SDL_Init.argtypes = (ctypes.c_int,)
    libsdl2.SDL_DestroyTexture.argtypes = (ctypes.c_void_p,)
    libsdl2.SDL_QueryTexture.argtypes = (
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p)

    libsdl2_image.IMG_LoadTexture.argtypes = ctypes.c_void_p, ctypes.c_char_p
    libsdl2_image.IMG_LoadTexture.restype = ctypes.c_void_p

    sdl_init_everything = 62001
    if libsdl2.SDL_Init(sdl_init_everything) < 0:
        raise Error

    img_init_png = 2
    if libsdl2_image.IMG_Init(img_init_png) < 0:
        raise Error


def quit_subsystems() -> None:
    libsdl2_image.IMG_Quit()
    libsdl2.SDL_Quit()


class EventHandler:
    __slots__ = 'keyboard', 'quit_requested'

    def __init__(self, keyboard: Optional[Keyboard] = None) -> None:
        self.keyboard = keyboard or Keyboard()
        self.quit_requested = False

    def update(self) -> None:
        self.keyboard.update_keys()
        self.handle_pending_events()

    def handle_pending_events(self) -> None:
        for event in EventHandler.pending_events():
            if event.type == EventType.KEY_DOWN or event.type == EventType.KEY_UP:
                self.keyboard.update(event)
            elif event.type == EventType.QUIT:
                self.quit_requested = True

    @staticmethod
    def pending_events() -> Iterator[RawEvent]:
        event = RawEvent()
        while libsdl2.SDL_PollEvent(ctypes.byref(event)):
            yield event


class RawKeyboardEvent(ctypes.Structure):
    _fields_ = [
        ('type', ctypes.c_uint32),
        ('timestamp', ctypes.c_uint32),
        ('windowID', ctypes.c_uint32),
        ('state', ctypes.c_uint8),
        ('repeat', ctypes.c_uint8),
        ('padding2', ctypes.c_uint8),
        ('padding3', ctypes.c_uint8),
        ('keysym', ctypes.c_uint32),
    ]


class RawEvent(ctypes.Union):
    # noinspection PyTypeChecker
    _fields_ = [
        ('type', ctypes.c_uint32),
        ('key', RawKeyboardEvent),
        ('padding', ctypes.c_uint8 * 56),
    ]


@enum.unique
class KeyState(enum.Enum):
    PRESSED = enum.auto()
    DOWN = enum.auto()
    RELEASED = enum.auto()
    UP = enum.auto()


class Keyboard:
    __slots__ = 'keys'

    def __init__(self) -> None:
        self.keys = DefaultDict[Scancode, KeyState](lambda: KeyState.UP)

    def update(self, event: Optional[RawEvent]) -> None:
        self.update_keys()
        self.handle_event(event)

    def update_keys(self) -> None:
        for key, state in self.keys.items():
            if state is KeyState.RELEASED:
                self.keys[key] = KeyState.UP
            if state is KeyState.PRESSED:
                self.keys[key] = KeyState.DOWN

    def handle_event(self, event: Optional[RawEvent]) -> None:
        if not event or event.key.repeat:
            return

        if event.type == EventType.KEY_DOWN:
            self.keys[event.key.keysym] = KeyState.PRESSED
        elif event.type == EventType.KEY_UP:
            self.keys[event.key.keysym] = KeyState.RELEASED

    def key_state(self, scancode: Scancode) -> KeyState:
        return self.keys[scancode]

    def key_pressed(self, scancode: Scancode) -> bool:
        return self.key_state(scancode) is KeyState.PRESSED

    def key_down(self, scancode: Scancode) -> bool:
        return self.key_state(scancode) is KeyState.DOWN

    def key_released(self, scancode: Scancode) -> bool:
        return self.key_state(scancode) is KeyState.RELEASED

    def key_up(self, scancode: Scancode) -> bool:
        return self.key_state(scancode) is KeyState.UP


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


def raw_rectangle_parameter(rectangle: Rectangle) -> RawRect:
    return RawRect(
        int(rectangle.upper_left.real), int(rectangle.upper_left.imag),
        int(rectangle.dimensions.real), int(rectangle.dimensions.imag))


class RawRect(ctypes.Structure):
    _fields_ = [
        ('x', ctypes.c_int), ('y', ctypes.c_int),
        ('w', ctypes.c_int), ('h', ctypes.c_int)
    ]


def get_current_time() -> int:
    return cast(int, libsdl2.SDL_GetTicks())


class Destroyable(ABC):
    @abstractmethod
    def destroy(self) -> None:
        pass


class Window(Destroyable):
    __slots__ = 'raw_window'

    def __init__(self, title: bytes, dimensions: complex) -> None:
        x = int(dimensions.real / 2)
        y = int(dimensions.imag / 2)
        self.raw_window = libsdl2.SDL_CreateWindow(title, x, y, int(dimensions.real), int(dimensions.imag), 0)
        if not self.raw_window:
            raise Error

    def destroy(self) -> None:
        libsdl2.SDL_DestroyWindow(self.raw_window)

    def renderer(self, draw_color: Optional[Color] = None) -> Renderer:
        return Renderer(self, draw_color)


class Texture(Destroyable):
    __slots__ = 'raw_texture'

    def __init__(self, renderer: Renderer, path: bytes) -> None:
        self.raw_texture = libsdl2_image.IMG_LoadTexture(renderer.raw_renderer, path)
        if not self.raw_texture:
            raise Error

    @property
    def height(self) -> int:
        h = ctypes.c_int(0)
        if libsdl2.SDL_QueryTexture(self.raw_texture, None, None, None, ctypes.byref(h)) < 0:
            raise Error

        return h.value

    @property
    def width(self) -> int:
        w = ctypes.c_int(0)
        if libsdl2.SDL_QueryTexture(self.raw_texture, None, None, ctypes.byref(w), None) < 0:
            raise Error

        return w.value

    @property
    def dimensions(self) -> complex:
        return complex(self.width, self.height)

    def destroy(self) -> None:
        libsdl2.SDL_DestroyTexture(self.raw_texture)


LoadedTextures = Dict[bytes, Texture]


class Renderer(Destroyable):
    __slots__ = 'raw_renderer'

    def __init__(self, window: Window, draw_color: Optional[Color] = None) -> None:
        self.raw_renderer = libsdl2.SDL_CreateRenderer(window.raw_window, -1, 0)
        if not self.raw_renderer:
            raise Error
        self.set_draw_color(draw_color or Color.white())
        self.enable_alpha_blending()

    def destroy(self) -> None:
        libsdl2.SDL_DestroyRenderer(self.raw_renderer)

    def load_texture(self, path: bytes) -> Texture:
        return Texture(self, path)

    def load_textures(self, paths: List[bytes]) -> LoadedTextures:
        return {path: self.load_texture(path) for path in paths}

    def clear(self) -> None:
        if libsdl2.SDL_RenderClear(self.raw_renderer) < 0:
            raise Error

    def present(self) -> None:
        if libsdl2.SDL_RenderPresent(self.raw_renderer) < 0:
            raise Error

    def draw_rectangle(self, rectangle: Rectangle, fill: bool) -> None:
        if fill:
            if libsdl2.SDL_RenderFillRect(self.raw_renderer, ctypes.byref(raw_rectangle_parameter(rectangle))) < 0:
                raise Error
        else:
            raise NotImplementedError

    def draw_line(self, line: Line) -> None:
        if libsdl2.SDL_RenderDrawLine(
                self.raw_renderer, int(line.origin.real), int(line.origin.imag),
                int(line.end.real), int(line.end.imag)) < 0:
            raise Error

    def get_draw_color(self) -> Color:
        r = ctypes.c_int()
        g = ctypes.c_int()
        b = ctypes.c_int()
        a = ctypes.c_int()

        if libsdl2.SDL_GetRenderDrawColor(
                self.raw_renderer,
                ctypes.byref(r), ctypes.byref(g), ctypes.byref(b), ctypes.byref(a)) < 0:
            raise Error

        return Color(r.value, g.value, b.value, a.value)

    def set_draw_color(self, color: Color) -> None:
        if libsdl2.SDL_SetRenderDrawColor(self.raw_renderer, color.r, color.g, color.b, color.a) < 0:
            raise Error

    def enable_alpha_blending(self) -> None:
        if libsdl2.SDL_SetRenderDrawBlendMode(self.raw_renderer, 1) < 0:
            raise Error

    def draw_texture(
            self, texture: Texture,
            source: Rectangle, destination: Rectangle,
            flip: Flip = Flip.NONE) -> None:
        if libsdl2.SDL_RenderCopyEx(
                self.raw_renderer, texture.raw_texture,
                ctypes.byref(raw_rectangle_parameter(source)), ctypes.byref(raw_rectangle_parameter(destination)),
                ctypes.c_double(0), None, flip) < 0:
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
