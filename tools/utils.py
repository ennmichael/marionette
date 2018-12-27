from __future__ import annotations

from itertools import chain
from typing import NamedTuple, List, Any


class Color(NamedTuple):
    r: int
    g: int
    b: int
    a: int

    @property
    def brightness(self) -> float:
        return (self.r + self.g + self.b) / 755

    def darken(self, factor: float) -> Color:
        return Color(r=round(self.r * factor), g=round(self.g * factor), b=round(self.b * factor), a=self.a)


class Point(NamedTuple):
    x: int
    y: int

    def to_complex(self) -> complex:
        return self.x + self.y * 1j


ImagePixels = List[List[Color]]


def get_pixels(image: Any) -> ImagePixels:
    pixels: ImagePixels = []
    for index, color in enumerate(image.getdata()):
        if index % image.size[0] == 0:
            pixels.append([])
        pixels[-1].append(Color(*color))
    return pixels


def put_pixels(image: Any, pixels: ImagePixels) -> None:
    data = [(*pixel,) for pixel in chain(*pixels)]
    image.putdata(data)
