import unittest
from typing import List

from PIL import Image

from engine.graphics import scale_rectangle, scale_line, find_outline, get_pixels
from engine.utils import Rectangle, Line


class GraphicsTests(unittest.TestCase):
    def test_rectangle_scaling(self) -> None:
        view = Rectangle(upper_left=0, dimensions=100 + 100j)
        new_dimensions = 400 + 400j
        result = scale_rectangle(view, Rectangle(upper_left=0, dimensions=20 + 30j), new_dimensions)
        self.assertAlmostEqual(result.upper_left.real, 0)
        self.assertAlmostEqual(result.upper_left.imag, 0)
        self.assertAlmostEqual(result.dimensions.real, 80)
        self.assertAlmostEqual(result.dimensions.imag, 120)
        new_dimensions = 50 + 50j
        result = scale_rectangle(view, Rectangle(upper_left=0, dimensions=30 + 40j), new_dimensions)
        self.assertAlmostEqual(result.upper_left.real, 0)
        self.assertAlmostEqual(result.upper_left.imag, 0)
        self.assertAlmostEqual(result.dimensions.real, 15)
        self.assertAlmostEqual(result.dimensions.imag, 20)
        view = Rectangle(upper_left=20 + 30j, dimensions=150 + 150j)
        new_dimensions = 300 + 300j
        result = scale_rectangle(view, Rectangle(upper_left=10 - 20j, dimensions=30 + 40j), new_dimensions)
        self.assertAlmostEqual(result.upper_left.real, -20)
        self.assertAlmostEqual(result.upper_left.imag, -100)
        self.assertAlmostEqual(result.dimensions.real, 60)
        self.assertAlmostEqual(result.dimensions.imag, 80)
        view = Rectangle(upper_left=18 - 9j, dimensions=150 + 150j)
        new_dimensions = 50 + 50j
        result = scale_rectangle(view, Rectangle(upper_left=-9 + 12j, dimensions=30 + 90j), new_dimensions)
        self.assertAlmostEqual(result.upper_left.real, -9)
        self.assertAlmostEqual(result.upper_left.imag, 7)
        self.assertAlmostEqual(result.dimensions.real, 10)
        self.assertAlmostEqual(result.dimensions.imag, 30)

    def test_line_scaling(self) -> None:
        view = Rectangle(upper_left=0, dimensions=100 + 100j)
        new_dimensions = 400 + 400j
        result = scale_line(view, Line.create_at(origin=0, end=20 + 30j), new_dimensions)
        self.assertAlmostEqual(result.origin.real, 0)
        self.assertAlmostEqual(result.origin.imag, 0)
        self.assertAlmostEqual(result.end.real, 80)
        self.assertAlmostEqual(result.end.imag, 120)
        new_dimensions = 50 + 50j
        result = scale_line(view, Line.create_at(origin=0, end=30 + 40j), new_dimensions)
        self.assertAlmostEqual(result.origin.real, 0)
        self.assertAlmostEqual(result.origin.imag, 0)
        self.assertAlmostEqual(result.end.real, 15)
        self.assertAlmostEqual(result.end.imag, 20)
        view = Rectangle(upper_left=20 + 30j, dimensions=150 + 150j)
        new_dimensions = 300 + 300j
        result = scale_line(view, Line.create_at(origin=10 - 20j, end=30 + 40j), new_dimensions)
        self.assertAlmostEqual(result.origin.real, -20)
        self.assertAlmostEqual(result.origin.imag, -100)
        self.assertAlmostEqual(result.end.real, 60)
        self.assertAlmostEqual(result.end.imag, 80)
        view = Rectangle(upper_left=18 - 9j, dimensions=150 + 150j)
        new_end = 50 + 50j
        result = scale_line(view, Line.create_at(origin=-9 + 12j, end=30 + 90j), new_end)
        self.assertAlmostEqual(result.origin.real, -9)
        self.assertAlmostEqual(result.origin.imag, 7)
        self.assertAlmostEqual(result.end.real, 10)
        self.assertAlmostEqual(result.end.imag, 30)

    def test_outline(self) -> None:
        def load_outline(filename: str) -> List[complex]:
            with Image.open(filename) as image:
                return list(find_outline(get_pixels(image)))

        rectangle_outline = [
            2 + 2j, 3 + 2j, 4 + 2j, 5 + 2j,
            5 + 3j, 5 + 4j,
            5 + 5j, 4 + 5j, 3 + 5j, 2 + 5j,
            2 + 4j, 2 + 3j,
        ]
        self.assertEqual(load_outline('res/rectangle.png'), rectangle_outline)
        self.assertEqual(load_outline('res/rectangle_filled.png'), rectangle_outline)
        self.assertEqual(load_outline('res/rectangle_somewhat_filled.png'), rectangle_outline)

        circle_outline = [
            3 + 1j, 4 + 1j, 5 + 2j, 6 + 3j, 6 + 4j, 5 + 5j,
            4 + 6j, 3 + 6j, 2 + 5j, 1 + 4j, 1 + 3j, 2 + 2j,
        ]
        self.assertEqual(load_outline('res/circle.png'), circle_outline)
        self.assertEqual(load_outline('res/circle_filled.png'), circle_outline)

        self.assertEqual(load_outline('res/shape1.png'), [
            2 + 1j, 3 + 1j, 4 + 1j, 5 + 2j, 5 + 3j, 6 + 4j, 7 + 4j,
            7 + 5j, 7 + 6j, 7 + 7j, 6 + 7j, 5 + 7j, 4 + 7j, 3 + 7j,
            2 + 7j, 1 + 7j, 1 + 6j, 1 + 5j, 2 + 4j, 2 + 3j, 2 + 2j,
        ])

        self.assertEqual(load_outline('res/shape2.png'), [
            4 + 0j, 5 + 0j, 6 + 0j, 6 + 1j, 6 + 2j, 6 + 3j, 6 + 4j,
            6 + 5j, 5 + 6j, 4 + 6j, 3 + 6j, 2 + 6j, 2 + 5j, 2 + 4j,
            3 + 4j, 4 + 3j, 5 + 2j, 4 + 1j, 3 + 1j, 2 + 1j, 1 + 1j,
            2 + 1j, 3 + 1j,
        ])

        self.assertEqual(load_outline('res/shape3.png'), [
            2 + 0j, 3 + 0j, 4 + 0j, 5 + 0j, 6 + 1j, 6 + 2j, 6 + 3j,
            6 + 4j, 6 + 5j, 6 + 6j, 6 + 7j, 5 + 7j, 4 + 7j, 4 + 6j,
            4 + 5j, 4 + 4j, 3 + 3j, 2 + 4j, 1 + 4j, 0 + 5j, 0 + 4j,
            0 + 3j, 0 + 2j, 0 + 1j, 1 + 1j,
        ])


if __name__ == '__main__':
    unittest.main()
