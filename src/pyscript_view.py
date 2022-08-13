"""ゲームビュー(pyscript)."""
import math

from js import (
    console,
    document,
    Element,
    CanvasRenderingContext2D,
)
from pyodide import create_proxy

from pyscript_controller import GameController
from game import GameModel
from ban import Ban
from values import Cell, StoneColor

#: 石の色
_STONE_COLORS = {
    StoneColor.Red: 'rgb(200, 0, 0)',
    StoneColor.Green: 'rgb(0, 200, 0)',
    StoneColor.Blue: 'rgb(0, 0, 200)',
    StoneColor.Yellow: 'rgb(200, 200, 0)',
}

#: arc開始角度
_ANGLE_START = 0 * math.pi / 180
#: arc終了角度
_ANGLE_END = 360 * math.pi / 180


def draw_line(ctx: CanvasRenderingContext2D, start_pos: tuple[int, int], end_pos: tuple[int, int]):
    """線の描画."""
    ctx.beginPath()
    ctx.moveTo(*start_pos)
    ctx.lineTo(*end_pos)
    ctx.stroke()
    ctx.closePath()


def draw_stone(ctx: CanvasRenderingContext2D, center: tuple[int, int], radius: int, color: StoneColor):
    """石の描画."""
    (x, y) = center
    ctx.beginPath()
    ctx.fillStyle = _STONE_COLORS[color]
    ctx.arc(x, y, radius, _ANGLE_START, _ANGLE_END)
    ctx.fill()
    ctx.closePath()


class ResultView:
    """結果表示ビュー."""

    def __init__(self, model: GameModel, ctx: CanvasRenderingContext2D):
        self._model = model
        self._ctx = ctx

    def draw(self) -> None:
        """描画."""
        if self._model.is_waitstart():
            text = 'Press MouseLeft to Start'
            self._ctx.font = '28px bold sans-serif'

            self._ctx.fillStyle = 'rgb(0, 0, 0)'
            self._ctx.fillText(text, 37, 182)
            self._ctx.fillStyle = 'rgb(255, 255, 255)'
            self._ctx.fillText(text, 35, 180)
        elif self._model.is_gameover():
            text = 'GameOver !'
            self._ctx.font = '60px bold sans-serif'

            self._ctx.fillStyle = 'rgb(0, 0, 0)'
            self._ctx.fillText(text, 37, 202)
            self._ctx.fillStyle = 'rgb(255, 0, 0)'
            self._ctx.fillText(text, 35, 200)
        elif self._model.is_success():
            text = 'Success !'
            self._ctx.font = '60px bold sans-serif'

            self._ctx.fillStyle = 'rgb(0, 0, 0)'
            self._ctx.fillText(text, 57, 202)
            self._ctx.fillStyle = 'rgb(0, 255, 255)'
            self._ctx.fillText(text, 55, 200)


class NextStoneView:
    """次の石ビュー."""

    def __init__(self, model: GameModel, ctx: CanvasRenderingContext2D):
        self._model = model
        self._ctx = ctx

    def draw(self) -> None:
        """描画."""

        # テキスト
        self._ctx.fillStyle = "rgb(0, 0, 0)"
        self._ctx.font = "30px bold sans-serif"
        self._ctx.fillText('Next', 440, 80)

        # 石
        pos = (535, 70)
        radius = 15
        draw_stone(self._ctx, pos, radius, self._model.next_stone)


class TimerView:
    """経過時間ビュー."""

    def __init__(self, model: GameModel, ctx: CanvasRenderingContext2D):
        self._model = model
        self._ctx = ctx

    def draw(self) -> None:
        """描画."""

        self._ctx.font = "30px bold sans-serif"
        self._ctx.fillStyle = "rgb(0, 0, 0)"
        self._ctx.fillText(f'Time:{self._model.time_sec}', 440, 250)


class BanView:
    """盤用ビュー."""

    def __init__(self, ban: Ban, ctx: CanvasRenderingContext2D):
        if ban is None:
            raise ValueError()
        self._ban = ban
        self._ctx = ctx

    def draw(self) -> None:
        """描画."""
        margin = self._ban.margin
        cell_size = (self._ban.size - margin * 2) / self._ban.cell_num

        # 土台
        self._ctx.fillStyle = "rgb(200, 100, 0)"
        self._ctx.fillRect(0, 0, self._ban.size, self._ban.size)

        # マスの枠
        self._ctx.strokeStyle = "rgb(0, 0, 0)"
        self._ctx.lineWidth = 2
        for x in range(self._ban.cell_num + 1):
            start_pos = (x * cell_size + margin, 0 + margin)
            end_pos = (x * cell_size + margin, self._ban.size - margin)
            draw_line(self._ctx, start_pos, end_pos)
        for y in range(self._ban.cell_num + 1):
            start_pos = (margin, y * cell_size + margin)
            end_pos = (self._ban.size - margin, y * cell_size + margin)
            draw_line(self._ctx, start_pos, end_pos)
            
        # 石
        for row in range(self._ban.cell_num):
            for column in range(self._ban.cell_num):
                color = self._ban.get(Cell(row, column))
                if color == 0:
                    continue
                offset = margin + cell_size / 2
                center_x = column * cell_size + offset
                center_y = row * cell_size + offset
                radius = 15
                self._ctx.beginPath()
                self._ctx.fillStyle = _STONE_COLORS[color]
                self._ctx.arc(center_x, center_y, radius, _ANGLE_START, _ANGLE_END)
                self._ctx.fill()
                self._ctx.closePath()


class GameView:
    """ゲームのビュー.

    :param model: ゲームモデル
    :param canvas: 描画先のCanvas
    :param controller: コントローラー
    """

    #: 背景色
    BACK_GROUND_COLOR = 'rgb(255, 255, 200)'
    #: フォントの標準色
    FONT_COLOR = 'rgb(0, 0, 0)'
    #: 画面幅
    WIDTH = 600
    #: 画面高さ
    HEIGHT = 400

    def __init__(
            self,
            model: GameModel,
            canvas: Element,
            controller: GameController) -> None:
        console.log('[GameView] Create')

        if model is None:
            raise ValueError('model is None')
        self._model = model

        self._setup_view(canvas)
        self._register_input_events(canvas, controller)

    def _setup_view(self, canvas: Element) -> None:
        """ビューの初期化."""
        if canvas is None:
            raise ValueError('canvas is None')
        canvas.width = GameView.WIDTH
        canvas.height = GameView.HEIGHT

        self._ctx = canvas.getContext('2d')
        if self._ctx is None:
            raise ValueError('ctx is None')

        self._ban = BanView(self._model.ban, self._ctx)
        self._timer = TimerView(self._model, self._ctx)
        self._next_stone = NextStoneView(self._model, self._ctx)
        self._result = ResultView(self._model, self._ctx)

    @staticmethod
    def _register_input_events(canvas: Element, controller: GameController) -> None:
        """入力イベントを登録する."""
        canvas.addEventListener("mousedown", create_proxy(controller.mousedown))
        canvas.addEventListener("mouseup", create_proxy(controller.mouseup))
        canvas.addEventListener("mousemove", create_proxy(controller.mousemove))

        # キーイベントはelementでは取れないのでdocumentに登録する必要がある
        document.addEventListener("keydown", create_proxy(controller.keydown))
        document.addEventListener("keyup", create_proxy(controller.keyup))

    def draw(self) -> None:
        """描画."""
        self._clear()
        self._ban.draw()
        self._timer.draw()
        self._next_stone.draw()
        self._result.draw()

    def _clear(self) -> None:
        """画面をクリアする."""
        self._ctx.fillStyle = GameView.BACK_GROUND_COLOR
        self._ctx.fillRect(0, 0, GameView.WIDTH, GameView.HEIGHT)
