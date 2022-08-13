"""三目不並：アプリケーション."""
import time

from game import GameModel
from pygame_view import GameView

#: ゲームのFPS
_FPS = 1.0 / 30.0
#: スクリーン幅
_SCR_W = 600
#: スクリーン高さ
_SCR_H = 400
#: 盤の大きさ
_BAN_SIZE = 400
#: 盤のマス数
_BAN_CELL_NUM = 9
#: 盤の余白
_BAN_MARGIN = 10
#: 失敗判定となる数
_BAN_FAIL_NUM = 3


def main():
    """メイン関数."""
    model = GameModel(_BAN_SIZE, _BAN_CELL_NUM, _BAN_MARGIN, _BAN_FAIL_NUM)
    view = GameView(model, _SCR_W, _SCR_H)

    while True:
        if not model.update(_FPS):
            return
        if not view.update():
            return
        time.sleep(_FPS)


if __name__ == "__main__":
    main()
