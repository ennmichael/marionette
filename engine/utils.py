from __future__ import annotations

from typing import NamedTuple


# TODO Test me
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


def normalized(c: complex) -> complex:
    intensity = abs(c)
    return c / intensity


# TODO Test me
def point_in_rectangle(point: complex, rect: Rectangle) -> bool:
    upper_left = rect.upper_left
    lower_right = rect.lower_right
    return (upper_left.real <= point.real <= lower_right.real and
            upper_left.imag <= point.imag <= lower_right.imag)
