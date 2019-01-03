import unittest

from engine.graphics import scale_rectangle, scale_line
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
        result = scale_line(view, Line.from_to(origin=0, end=20 + 30j), new_dimensions)
        self.assertAlmostEqual(result.origin.real, 0)
        self.assertAlmostEqual(result.origin.imag, 0)
        self.assertAlmostEqual(result.end.real, 80)
        self.assertAlmostEqual(result.end.imag, 120)
        new_dimensions = 50 + 50j
        result = scale_line(view, Line.from_to(origin=0, end=30 + 40j), new_dimensions)
        self.assertAlmostEqual(result.origin.real, 0)
        self.assertAlmostEqual(result.origin.imag, 0)
        self.assertAlmostEqual(result.end.real, 15)
        self.assertAlmostEqual(result.end.imag, 20)
        view = Rectangle(upper_left=20 + 30j, dimensions=150 + 150j)
        new_dimensions = 300 + 300j
        result = scale_line(view, Line.from_to(origin=10 - 20j, end=30 + 40j), new_dimensions)
        self.assertAlmostEqual(result.origin.real, -20)
        self.assertAlmostEqual(result.origin.imag, -100)
        self.assertAlmostEqual(result.end.real, 20)
        self.assertAlmostEqual(result.end.imag, 20)
        view = Rectangle(upper_left=18 - 9j, dimensions=150 + 150j)
        new_end = 50 + 50j
        result = scale_line(view, Line.from_to(origin=-9 + 12j, end=30 + 90j), new_end)
        self.assertAlmostEqual(result.origin.real, -9)
        self.assertAlmostEqual(result.origin.imag, 7)
        self.assertAlmostEqual(result.end.real, 4)
        self.assertAlmostEqual(result.end.imag, 33)


if __name__ == '__main__':
    unittest.main()
