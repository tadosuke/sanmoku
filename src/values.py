"""値オブジェクトたち."""
from dataclasses import dataclass
from enum import Enum, IntEnum, auto


@dataclass
class Position:
    """座標."""
    x: int = 0
    y: int = 0

    def __str__(self):
        return f'({self.x}, {self.y})'

    def __eq__(self, other):
        if isinstance(other, Position):
            return self.x == other.x and self.y == other.y
        elif isinstance(other, tuple):
            (x, y) = other
            return self.x == x and self.y == y
        else:
            self == other


class Cell:
    """マス目."""

    def __init__(self, row: int, column: int) -> None:
        if row < 0:
            raise ValueError()
        if column < 0:
            raise ValueError()
        self._row: int = row
        self._column: int = column

    @property
    def row(self) -> int:
        return self._row

    @property
    def column(self) -> int:
        return self._column

    def get(self) -> tuple[int, int]:
        return self._row, self.column

    def __str__(self) -> str:
        return f'Cell({self.row}, {self.column})'

    def __repr__(self) -> str:
        return f'Cell({self.row}, {self.column})'

    def __eq__(self, other) -> bool:
        if isinstance(other, Cell):
            return self.row == other.row and self.column == other.column
        else:
            return self == other


class StoneColor(IntEnum):
    """石の色."""
    Min = 1
    Red = 1
    Green = 2
    Blue = 3
    Yellow = 4
    Max = 4


class GameMode(Enum):
    """ゲームモード."""
    WaitStart = auto()
    InGame = auto()
    Success = auto()
    GameOver = auto()

