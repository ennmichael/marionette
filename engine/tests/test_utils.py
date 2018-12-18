import unittest

from engine.utils import Rectangle, Line


class RectangleTests(unittest.TestCase):
    def test_corners(self) -> None:
        r = Rectangle(upper_left=10 + 2j, dimensions=2 + 3j)
        self.assertEqual(r.upper_left, 10 + 2j)
        self.assertEqual(r.upper_right, 12 + 2j)
        self.assertEqual(r.lower_left, 10 + 5j)
        self.assertEqual(r.lower_right, 12 + 5j)
        self.assertEqual(r.upper_imag, 2)
        self.assertEqual(r.lower_imag, 5)
        self.assertEqual(r.left_real, 10)
        self.assertEqual(r.right_real, 12)
        r.left_real = 6
        self.assertEqual(r.upper_left, 6 + 2j)
        self.assertEqual(r.upper_right, 8 + 2j)
        self.assertEqual(r.lower_left, 6 + 5j)
        self.assertEqual(r.lower_right, 8 + 5j)
        self.assertEqual(r.upper_imag, 2)
        self.assertEqual(r.lower_imag, 5)
        self.assertEqual(r.left_real, 6)
        self.assertEqual(r.right_real, 8)
        r.right_real = 12
        self.assertEqual(r.upper_left, 10 + 2j)
        self.assertEqual(r.upper_right, 12 + 2j)
        self.assertEqual(r.lower_left, 10 + 5j)
        self.assertEqual(r.lower_right, 12 + 5j)
        self.assertEqual(r.upper_imag, 2)
        self.assertEqual(r.lower_imag, 5)
        self.assertEqual(r.left_real, 10)
        self.assertEqual(r.right_real, 12)
        r.upper_imag = 3
        self.assertEqual(r.upper_left, 10 + 3j)
        self.assertEqual(r.upper_right, 12 + 3j)
        self.assertEqual(r.lower_left, 10 + 6j)
        self.assertEqual(r.lower_right, 12 + 6j)
        self.assertEqual(r.upper_imag, 3)
        self.assertEqual(r.lower_imag, 6)
        self.assertEqual(r.left_real, 10)
        self.assertEqual(r.right_real, 12)
        r.lower_imag = 5
        self.assertEqual(r.upper_left, 10 + 2j)
        self.assertEqual(r.upper_right, 12 + 2j)
        self.assertEqual(r.lower_left, 10 + 5j)
        self.assertEqual(r.lower_right, 12 + 5j)
        self.assertEqual(r.upper_imag, 2)
        self.assertEqual(r.lower_imag, 5)
        self.assertEqual(r.left_real, 10)
        self.assertEqual(r.right_real, 12)

    def test_line_intersects(self) -> None:
        line = Line(start=0.5 + 6j, offset=4.5 - 6j)
        self.assertFalse(line.intersects(Line(start=0, offset=1 + 2j)))
        self.assertFalse(Line(start=0, offset=1 + 2j).intersects(line))
        self.assertFalse(line.intersects(Line(start=0, offset=0.1 + 0.2j)))
        self.assertFalse(Line(start=0, offset=0.1 + 0.2j).intersects(line))
        self.assertTrue(line.intersects(Line(start=0, offset=2 + 4j)))
        self.assertTrue(Line(start=0, offset=2 + 4j).intersects(line))
        self.assertTrue(line.intersects(Line(start=0, offset=5 + 6j)))
        self.assertTrue(Line(start=0, offset=5 + 6j).intersects(line))
        self.assertTrue(line.intersects(Line(start=2 + 4j, offset=1 + 0.2j)))
        self.assertTrue(Line(start=2 + 4j, offset=1 + 0.2j).intersects(line))
        self.assertTrue(line.intersects(Line(start=2 + 4j, offset=-1 + 0.2j)))
        self.assertTrue(Line(start=2 + 4j, offset=-1 + 0.2j).intersects(line))
        line = Line(start=0, offset=5)
        self.assertFalse(line.intersects(Line.create_at(start=-2 - 2j, end=-1 - 1j)))
        self.assertFalse(Line.create_at(start=-2 - 2j, end=-1 - 1j).intersects(line))
        self.assertTrue(line.intersects(Line.create_at(start=-2 - 2j, end=0)))
        self.assertTrue(Line.create_at(start=-2 - 2j, end=0).intersects(line))
        self.assertTrue(line.intersects(Line.create_at(start=-2 + 1j, end=1)))
        self.assertTrue(Line.create_at(start=-2 + 1j, end=1).intersects(line))
        self.assertTrue(line.intersects(Line.create_at(start=1 + 2j, end=4 - 1j)))
        self.assertTrue(Line.create_at(start=1 + 2j, end=4 - 1j).intersects(line))
        self.assertTrue(line.intersects(Line.create_at(start=0 - 2j, end=1 + 2j)))
        self.assertTrue(Line.create_at(start=0 - 2j, end=1 + 2j).intersects(line))
        self.assertTrue(line.intersects(Line.create_at(start=1 + 2j, end=5)))
        self.assertTrue(Line.create_at(start=1 + 2j, end=5).intersects(line))
        line = Line(start=0, offset=5j)
        self.assertFalse(line.intersects(Line.create_at(start=-2, end=-1)))
        self.assertFalse(Line.create_at(start=-2, end=-1).intersects(line))
        self.assertFalse(line.intersects(Line.create_at(start=-2, end=-1 + 1j)))
        self.assertFalse(Line.create_at(start=-2, end=-1 + 1j).intersects(line))
        self.assertTrue(line.intersects(Line.create_at(start=-2, end=0)))
        self.assertTrue(Line.create_at(start=-2, end=0).intersects(line))
        self.assertTrue(line.intersects(Line.create_at(start=-2, end=5j)))
        self.assertTrue(Line.create_at(start=-2, end=5j).intersects(line))
        self.assertTrue(line.intersects(Line.create_at(start=-2, end=1 + 1j)))
        self.assertTrue(line.intersects(Line.create_at(start=-1 + 4j, end=1 + 4j)))
        self.assertTrue(line.intersects(Line.create_at(start=0, end=1 + 1j)))
        self.assertTrue(line.intersects(Line.create_at(start=5j, end=1 + 1j)))

    def test_contains_point(self) -> None:
        r = Rectangle(upper_left=1 + 2j, dimensions=5 + 2j)
        for real in range(-10, 1):
            for imag in range(-10, 2):
                self.assertFalse(r.contains_point(real + imag * 1j))
            for imag in range(5, 10):
                self.assertFalse(r.contains_point(real + imag * 1j))
        for real in range(7, 11):
            for imag in range(-10, 2):
                self.assertFalse(r.contains_point(real + imag * 1j))
            for imag in range(4, 10):
                self.assertFalse(r.contains_point(real + imag * 1j))
        for real in range(1, 7):
            for imag in range(2, 5):
                self.assertTrue(r.contains_point(real + imag * 1j))


if __name__ == '__main__':
    unittest.main()
