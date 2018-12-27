#!/usr/bin/env python3

from __future__ import annotations

from abc import ABC, abstractmethod
from argparse import ArgumentParser
from contextlib import suppress
from typing import NamedTuple, List, Any, Iterable, Optional

from PIL import Image

from tools.utils import Color, Point, ImagePixels, get_pixels, put_pixels


def main() -> None:
    arguments = parse_arguments()

    if arguments.mode == 'equal':
        mode = EqualMode(arguments.max_passes)
    else:
        mode = DarkOnlyMode(arguments.min_alpha, arguments.max_brightness, arguments.max_passes)
    image = Image.open(arguments.infile)
    pixels = get_pixels(image)
    anti_alias(pixels, mode, arguments.factor)
    put_pixels(image, pixels)
    image.save(arguments.outfile)


def parse_arguments() -> Any:
    argument_parser = ArgumentParser()
    argument_parser.add_argument('infile')
    argument_parser.add_argument('outfile')
    argument_parser.add_argument('--mode', choices=['equal', 'dark_only'], default='equal')
    argument_parser.add_argument('--min_alpha', type=int, default=170)
    argument_parser.add_argument('--max_brightness', type=float, default=0.2)
    argument_parser.add_argument('--max_passes', type=int)
    argument_parser.add_argument('--factor', type=float, default=1.0)
    return argument_parser.parse_args()


class OperatingMode(ABC):
    @abstractmethod
    def accepts_neighbour(self, neighbour: Color, neighbours: List[Color]) -> bool:
        pass

    @abstractmethod
    def pass_again(self, border_pixels: List[BorderPixel], num_passes: int) -> bool:
        pass


class EqualMode(OperatingMode):
    def __init__(self, num_passes: Optional[int] = None) -> None:
        self.num_passes = num_passes or 1

    def accepts_neighbour(self, neighbour: Color, neighbours: List[Color]) -> bool:
        return neighbour not in neighbours

    def pass_again(self, border_pixels: List[BorderPixel], num_passes: int) -> bool:
        return num_passes < self.num_passes


class DarkOnlyMode(OperatingMode):
    def __init__(self, min_alpha: int, max_brightness: int, max_passes: Optional[int] = None) -> None:
        self.min_alpha = min_alpha
        self.max_brightness = max_brightness
        self.max_passes = max_passes

    def accepts_neighbour(self, neighbour: Color, neighbours: List[Color]) -> bool:
        return (neighbour.a >= self.min_alpha and
                neighbour.brightness <= self.max_brightness and
                neighbour not in neighbours)

    def pass_again(self, border_pixels: List[BorderPixel], num_passes: int) -> bool:
        if self.max_passes is not None:
            return num_passes < self.max_passes
        return bool(border_pixels)


class BorderPixel(NamedTuple):
    color: Color
    point: Point
    neighbours: List[Color]

    def anti_alias(self, factor: float) -> Color:
        color = self.color
        for neighbour in self.neighbours:
            color = Color(
                r=color.r + round(factor * neighbour.r), g=color.g + round(factor * neighbour.g),
                b=color.b + round(factor * neighbour.b), a=color.a + round(factor * neighbour.a))
        d = len(self.neighbours) + 1
        return Color(
            r=round(color.r / d), g=round(color.g / d),
            b=round(color.b / d), a=round(color.a / d))


def anti_alias(pixels: ImagePixels, mode: OperatingMode, factor: float = 1.0) -> None:
    num_passes = 0
    while True:
        border_pixels = list(find_border_pixels(pixels, mode))
        if not mode.pass_again(border_pixels, num_passes):
            return
        num_passes += 1
        for border_pixel in border_pixels:
            pixels[border_pixel.point.y][border_pixel.point.x] = border_pixel.anti_alias(factor)


def find_border_pixels(pixels: ImagePixels, mode: OperatingMode) -> Iterable[BorderPixel]:
    for y, row in enumerate(pixels):
        for x, color in enumerate(row):
            point = Point(x, y)
            neighbours = neighbour_pixels(pixels, point, mode)
            if len(neighbours) == 1:
                (single_neighbour,) = neighbours
                if single_neighbour == color:
                    continue
            yield BorderPixel(color, point, neighbours)


def neighbour_pixels(pixels: ImagePixels, point: Point, mode: OperatingMode) -> List[Color]:
    neighbours: List[Color] = []
    for neighbour_point in neighbour_points(point):
        with suppress(IndexError):
            neighbour = pixels[neighbour_point.y][neighbour_point.x]
            if mode.accepts_neighbour(neighbour, neighbours):
                neighbours.append(neighbour)
    return neighbours


def neighbour_points(point: Point) -> Iterable[Point]:
    yield Point(point.x - 1, point.y - 1)
    yield Point(point.x, point.y - 1)
    yield Point(point.x + 1, point.y - 1)
    yield Point(point.x + 1, point.y)
    yield Point(point.x + 1, point.y + 1)
    yield Point(point.x, point.y + 1)
    yield Point(point.x - 1, point.y + 1)
    yield Point(point.x - 1, point.y)


if __name__ == '__main__':
    main()
