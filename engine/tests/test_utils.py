import unittest

from engine.utils import Rectangle


class RectangleTests(unittest.TestCase):
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
