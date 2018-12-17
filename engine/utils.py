from __future__ import annotations

from typing import NamedTuple


class Rectangle(NamedTuple):
    upper_left: complex
    upper_right: complex
    lower_left: complex
    lower_right: complex
    dimensions: complex

    @staticmethod
    def create(upper_left: complex, dimensions: complex) -> Rectangle:
        upper_right = upper_left + dimensions.real
        lower_right = upper_right + dimensions.imag * 1j
        lower_left = upper_left + dimensions.imag * 1j
        return Rectangle(upper_left, upper_right, lower_left, lower_right, dimensions)

    def contains_point(self, point: complex) -> bool:
        return (self.upper_left.real <= point.real <= self.lower_right.real and
                self.upper_left.imag <= point.imag <= self.lower_right.imag)


# TODO Test me
def normalized(c: complex) -> complex:
    if c == 0:
        return 0
    intensity = abs(c)
    return c / intensity


def magnitude_squared(c: complex) -> float:
    return c.real * c.real + c.imag * c.imag
