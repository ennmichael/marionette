#!/usr/bin/env python3

from __future__ import annotations

import enum
import cmath
from argparse import ArgumentParser
from typing import Any, Iterable, List, NamedTuple

from PIL import Image

from tools.utils import ImagePixels, Color, Point, get_pixels, put_pixels
from engine.utils import cross_product, dot_product, normalized


def main() -> None:
    image = Image.open('in.png')
    pixels = get_pixels(image)
    lighting_direction = cmath.exp(1j * cmath.pi / 4)
    for x, y in list(find_lighted_outline(pixels, lighting_direction)):
        pixels[y][x] = Color(0, 0, 255, 255)
    shadow(pixels, 45.0)
    put_pixels(image, pixels)
    image.save('out.png')


def parse_arguments() -> Any:
    argument_parser = ArgumentParser()
    argument_parser.add_argument('infile')
    argument_parser.add_argument('outfile')
    return argument_parser.parse_args()


def shadow(pixels: ImagePixels, light_angle: complex) -> None:
    for outline_point in find_outline(pixels):
        cast_shadow(pixels, Ray(origin=outline_point.to_complex(), direction=light_angle))


def outline_starting_position(pixels: ImagePixels) -> Point:


def cast_shadow(pixels: ImagePixels, light_ray: Ray, darkness: float) -> None:
    light_ray = light_ray.opposite()
    while True:
        pixels[int(light_ray.origin.imag)][int(light_ray.origin.real)]


class Ray(NamedTuple):
    origin: complex
    direction: complex

    @property
    def x(self) -> int:

    def advance(self) -> Ray:
        return Ray(origin=self.origin + self.direction, direction=self.direction)

    def opposite(self) -> Ray:
        return Ray(self.origin, -self.direction)


if __name__ == '__main__':
    main()
