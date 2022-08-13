import unittest

from sanmoku.src.values import Cell, Position
from sanmoku.src.ban import Ban, SequenceCounter

#: 盤の大きさ
_SIZE = 400
#: 盤のマス数
_CELL_NUM = 9
#: 失敗判定となる数
_FAIL_NUM = 3
#: 盤の余白
_MARGIN = 10


class TestBan(unittest.TestCase):

    def setUp(self):
        self.ban = Ban(_SIZE, _CELL_NUM, _MARGIN, _FAIL_NUM)

    def test_init(self):
        ban = self.ban
        self.assertEqual(ban.size, 400)
        self.assertEqual(ban.cell_num, 9)
        self.assertEqual(ban._margin, _MARGIN)
        self.assertEqual(ban._fail_num, _FAIL_NUM)
        self.assertEqual(len(ban._cells), _CELL_NUM)
        self.assertEqual(len(ban._cells[0]), _CELL_NUM)
        self.assertEqual(ban._cell_size, 42)

    def test_put(self):
        ban = self.ban
        ban.put(Cell(0, 0), 1)
        self.assertEqual(ban.get(Cell(0, 0)), 1)
        ban.put(Cell(_CELL_NUM-1, _CELL_NUM-1), 1)
        self.assertEqual(ban.get(Cell(_CELL_NUM-1, _CELL_NUM-1)), 1)

        with self.assertRaises(ValueError):
            ban.put(Cell(_CELL_NUM, _CELL_NUM), 1)
            ban.put(Cell(-1, -1), 1)

    def test_is_in_range(self):
        ban = self.ban
        self.assertTrue(ban._is_in_range(Cell(0, 0)))
        self.assertTrue(ban._is_in_range(Cell(_CELL_NUM-1, _CELL_NUM-1)))
        self.assertFalse(ban._is_in_range(Cell(_CELL_NUM, 0)))
        self.assertFalse(ban._is_in_range(Cell(0, _CELL_NUM)))

    def test_is_fail_right(self):
        ban = self.ban
        self.assertFalse(ban.is_fail())
        ban.put(Cell(0, 0), 1)
        self.assertFalse(ban.is_fail())
        ban.put(Cell(0, 1), 1)
        self.assertFalse(ban.is_fail())
        ban.put(Cell(0, 2), 1)
        self.assertTrue(ban.is_fail())

    def test_is_fail_bottom(self):
        ban = self.ban
        self.assertFalse(ban.is_fail())
        ban.put(Cell(0, 0), 1)
        self.assertFalse(ban.is_fail())
        ban.put(Cell(1, 0), 1)
        self.assertFalse(ban.is_fail())
        ban.put(Cell(2, 0), 1)
        self.assertTrue(ban.is_fail())

    def test_is_fail_diagonal_rihgt(self):
        ban = self.ban
        self.assertFalse(ban.is_fail())
        ban.put(Cell(0, 0), 1)
        self.assertFalse(ban.is_fail())
        ban.put(Cell(1, 1), 1)
        self.assertFalse(ban.is_fail())
        ban.put(Cell(2, 2), 1)
        self.assertTrue(ban.is_fail())

    def test_is_fail_diagonal_left(self):
        ban = self.ban
        self.assertFalse(ban.is_fail())
        ban.put(Cell(0, 2), 1)
        self.assertFalse(ban.is_fail())
        ban.put(Cell(1, 1), 1)
        self.assertFalse(ban.is_fail())
        ban.put(Cell(2, 0), 1)
        self.assertTrue(ban.is_fail())

    def test_position_to_cell(self):
        ban = self.ban
        self.assertIsNone(ban.position_to_cell(Position(0, 0)))
        self.assertEqual(ban.position_to_cell(Position(10, 10)), Cell(0, 0))
        self.assertEqual(ban.position_to_cell(Position(52, 52)), Cell(1, 1))
        self.assertEqual(ban.position_to_cell(Position(94, 94)), Cell(2, 2))

    def test_is_success(self):
        ban = self.ban
        self.assertFalse(ban.is_success())
        for row in range(ban.cell_num):
            for column in range(ban.cell_num):
                ban.put(Cell(row, column), 1)
        self.assertTrue(ban.is_success())


class TestSequenceCounter(unittest.TestCase):

    def test_case(self):
        counter = SequenceCounter()
        self.assertEqual(counter.count(1), 1)
        self.assertEqual(counter.count(1), 2)
        self.assertEqual(counter.count(2), 1)
        self.assertEqual(counter.count(2), 2)


if __name__ == "__main__":
    unittest.main()
