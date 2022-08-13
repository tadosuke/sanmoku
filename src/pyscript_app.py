"""三目不並：アプリケーション（PyScript版）."""
import asyncio

from js import (
    console,
    document,
    Element,
)
from pyodide import create_proxy

from game import GameModel
from pyscript_controller import GameController
from pyscript_view import GameView


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


async def main() -> None:
    """メイン関数."""

    canvas = document.querySelector('#output')
    if canvas is None:
        console.error('context is None')
        return

    try:
        model = GameModel(_BAN_SIZE, _BAN_CELL_NUM, _BAN_MARGIN, _BAN_FAIL_NUM)
        controller = GameController(model)
        view = GameView(model, canvas, controller)

    except ValueError as e:
        console.error(f'Failed to create GameObjects:{e}')
        return

    while True:
        model.update(_FPS)
        view.draw()
        await asyncio.sleep(_FPS)


if __name__ == '__main__':
    pyscript_loader.close()
    pyscript.run_until_complete(main())
