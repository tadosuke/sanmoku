"""ゲームモデル."""
import random

from ban import Ban
from input import VirtualKey, OperationParam, InputState
from values import Position, Cell, StoneColor, GameMode


def get_next_stone() -> StoneColor:
    """次の石をランダムで得る."""
    return random.randint(StoneColor.Min, StoneColor.Max)  # type: ignore


class Timer:

    def __init__(self) -> None:
        self._sec: float = 0.0
        self._is_start = False

    def start(self) -> None:
        self._sec = 0.0
        self._is_start = True

    def stop(self) -> None:
        self._is_start = False

    def update(self, delta: float) -> None:
        if not self._is_start:
            return
        self._sec += delta

    def get_int(self) -> int:
        return int(self._sec)


class GameModel:
    """ゲーム本体."""

    def __init__(
            self,
            ban_size: int,
            ban_cell_num: int,
            ban_margin: int,
            ban_fail_num: int) -> None:
        print('[GameModel] Create')

        self._ban = Ban(ban_size, ban_cell_num, ban_margin, ban_fail_num)
        self._mouse_pos: Position = Position(0, 0)
        self._press = False
        self._mode = GameMode.WaitStart

        self._next = StoneColor.Min
        self._change_stone()
        self._timer = Timer()

    @property
    def time_sec(self) -> int:
        return self._timer.get_int()

    @property
    def ban(self):
        return self._ban

    @property
    def next_stone(self) -> StoneColor:
        return self._next

    def update(self, delta: float) -> bool:
        """定期更新処理.

        :param delta: デルタ秒
        :return: 終了時はFalse
        """
        self._timer.update(delta)

        return True

    def is_waitstart(self) -> bool:
        """ゲーム開始待ちか."""
        return self._mode == GameMode.WaitStart

    def is_gameover(self) -> bool:
        """ゲームオーバー状態か."""
        return self._mode == GameMode.GameOver

    def is_success(self) -> bool:
        """クリア状態か."""
        return self._mode == GameMode.Success

    def enable_control(self) -> bool:
        """操作可能か."""
        return self._mode == GameMode.WaitStart or self._mode == GameMode.InGame

    def operate(self, param: OperationParam) -> None:
        """入力時に外部から呼ばれる."""
        if not self.enable_control():
            return
        if param.code == VirtualKey.MouseLeft:
            if param.state == InputState.Press:
                if not self._press:
                    self._on_click(param.position)
                self._press = True
            elif param.state == InputState.Release:
                self._press = False

    def _on_click(self, pos: Position) -> None:
        """クリック時に呼ばれる."""
        if self.is_waitstart():
            self._mode = GameMode.InGame
            self._timer.start()
            return
        cell = self._ban.position_to_cell(pos)
        if cell is None:
            return
        # print(f'OnClick={cell}')
        self._put_stone(cell)

    def _put_stone(self, cell: Cell):
        if self._ban.put(cell, self._next):
            print(f'Put({self._next}) to {cell}')
            if self._ban.is_fail():
                print('GameOver!')
                self._mode = GameMode.GameOver
                self._timer.stop()
            elif self._ban.is_success():
                print('Success!')
                self._mode = GameMode.Success
                self._timer.stop()
            self._change_stone()

    def _change_stone(self):
        """石を替える."""
        self._next = get_next_stone()
