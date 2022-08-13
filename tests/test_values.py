import unittest

from sanmoku.src.values import Cell


class TestValues(unittest.TestCase):

    def test_cell(self):
        print('')
        cell = Cell(5, 7)
        self.assertEqual(cell.row, 5)
        self.assertEqual(cell.column, 7)
        self.assertEqual(cell.get(), (5, 7))
        print(cell)


if __name__ == "__main__":
    unittest.main()
