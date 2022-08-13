import typing as tp

from values import Cell, Position


class SequenceCounter:
    """連続した要素の個数を数える."""

    def __init__(self):
        self._pre = None
        self._num: int = 1

    def count(self, obj) -> int:
        if self._pre != obj:
            self._pre = obj
            self._num = 1
        else:
            self._num += 1
        return self._num


class Ban:
    """盤面.

    :param size: 盤の大きさ
    :param cell_num: 一辺のマス数
    :param margin: 盤の端からマスまでの余白
    :param fail_num: 失敗判定となる数
    """

    def __init__(self, size: int, cell_num: int, margin: int, fail_num: int) -> None:
        self._size = size
        self._cell_num = cell_num
        self._margin = margin
        self._fail_num = fail_num

        self._cells: tp.List[tp.List] = []
        for row in range(cell_num):
            self._cells.append([])
            for column in range(cell_num):
                self._cells[row].append(0)

    @property
    def size(self) -> int:
        """盤の大きさ."""
        return self._size

    @property
    def cell_num(self) -> int:
        """盤のマス数."""
        return self._cell_num

    @property
    def margin(self) -> int:
        return self._margin

    def display(self):
        print(self._cells)

    def get(self, cell: Cell) -> int:
        """指定位置の石を得る."""
        return self._cells[cell.row][cell.column]

    def put(self, cell: Cell, color) -> bool:
        """石を置く.

        :return: 置けたらTrue. 他の石があって置けない場合はFalse
        """
        if not self._is_in_range(cell):
            raise ValueError()

        if self._cells[cell.row][cell.column] == 0:
            self._cells[cell.row][cell.column] = color
            return True
        return False

    def _is_in_range(self, cell: Cell) -> bool:
        """指定した座標が範囲内か"""
        if cell.column < 0 or self._cell_num <= cell.column:
            return False
        if cell.row < 0 or self._cell_num <= cell.row:
            return False
        return True

    def position_to_cell(self, pos: Position) -> tp.Optional[Cell]:
        row = (pos.y - self._margin) / self._cell_size
        column = (pos.x - self._margin) / self._cell_size
        if row < 0 or column < 0:
            return None

        try:
            cell = Cell(int(row), int(column))
        except ValueError:
            return None

        if self._is_in_range(cell):
            return cell
        return None

    @property
    def _cell_size(self) -> int:
        return int((self._size - (self._margin * 2)) / self._cell_num)

    def is_fail(self) -> bool:
        """失敗判定"""
        for y in range(self._cell_num):
            for x in range(self._cell_num):
                if self._is_fail(x, y):
                    return True
        return False

    def _is_fail(self, x, y) -> bool:
        """指定地点からの判定"""
        start_max = self._cell_num - self._fail_num
        start_min = self._fail_num - 1

        # 右
        if x <= start_max:
            counter = SequenceCounter()
            for dx in range(self._fail_num):
                col = self._cells[y][x + dx]
                if col == 0:
                    break
                num = counter.count(col)
                if self._fail_num <= num:
                    return True

        # 下
        if y <= start_max:
            counter = SequenceCounter()
            for dy in range(self._fail_num):
                col = self._cells[y + dy][x]
                if col == 0:
                    break
                num = counter.count(col)
                if self._fail_num <= num:
                    return True

        # 右下
        if x <= start_max and y <= start_max:
            counter = SequenceCounter()
            for d in range(self._fail_num):
                col = self._cells[y + d][x + d]
                if col == 0:
                    break
                num = counter.count(col)
                if self._fail_num <= num:
                    return True

        # 左下
        if start_min <= x and y <= start_max:
            counter = SequenceCounter()
            for d in range(self._fail_num):
                col = self._cells[y + d][x - d]
                if col == 0:
                    break
                num = counter.count(col)
                if self._fail_num <= num:
                    return True

        return False

    def is_success(self) -> bool:
        """クリア状態か."""
        for row in self._cells:
            for cell in row:
                if cell == 0:
                    return False
        return True
