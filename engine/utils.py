from __future__ import annotations

from typing import NamedTuple

import math


class Rectangle(NamedTuple):
    upper_left: complex
    dimensions: complex

    @property
    def left_real(self) -> float:
        return self.upper_left.real

    @property
    def right_real(self) -> float:
        return self.upper_left.real + self.dimensions.real

    @property
    def upper_imag(self) -> float:
        return self.upper_left.imag

    @property
    def lower_imag(self) -> float:
        return self.upper_left.imag + self.dimensions.imag

    @property
    def upper_right(self) -> complex:
        return self.upper_left + self.dimensions.real

    @property
    def lower_left(self) -> complex:
        return self.upper_right + self.dimensions.imag * 1j

    @property
    def lower_right(self) -> complex:
        return self.upper_left + self.dimensions.imag * 1j

    # TODO Test the overlaps code
    def overlaps_on_real_axis(self, other: Rectangle) -> bool:
        return (other.left_real <= self.left_real <= other.right_real or
                other.left_real <= self.right_real <= other.right_real)

    def overlaps_on_imag_axis(self, other: Rectangle) -> bool:
        return (self.upper_imag <= other.upper_imag <= self.lower_imag or
                self.upper_imag <= other.lower_imag <= self.lower_imag)

    def overlaps(self, other: Rectangle) -> bool:
        return self.overlaps_on_real_axis(other) and self.overlaps_on_imag_axis(other)

    def contains_point(self, point: complex) -> bool:
        return (self.left_real <= point.real <= self.right_real and
                self.upper_imag <= point.imag <= self.lower_imag)


# TODO Test me
def normalized(c: complex) -> complex:
    if c == 0:
        return 0
    intensity = abs(c)
    return c / intensity


def magnitude_squared(c: complex) -> float:
    return c.real * c.real + c.imag * c.imag


def cross_product(c1: complex, c2: complex) -> float:
    return c1.real * c2.imag - c1.imag * c2.real


# TODO Add absolute / relative tolerance parameters (I think this is why I'm getting assertion errors)
def complex_is_close(a: complex, b: complex) -> bool:
    return math.isclose(a.real, b.real) and math.isclose(a.imag, b.imag)
