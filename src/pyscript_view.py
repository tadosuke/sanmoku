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

#: 石の半径
_STONE_RADIUS = 15


def draw_line(ctx: CanvasRenderingContext2D, start_pos: tuple[int, int], end_pos: tuple[int, int]) -> None:
    """線の描画."""
    ctx.beginPath()
    ctx.moveTo(*start_pos)
    ctx.lineTo(*end_pos)
    ctx.stroke()
    ctx.closePath()


def draw_stone(ctx: CanvasRenderingContext2D, center: tuple[int, int], color: StoneColor) -> None:
    """石の描画."""
    (x, y) = center
    ctx.beginPath()
    ctx.fillStyle = _STONE_COLORS[color]
    ctx.arc(x, y, _STONE_RADIUS, _ANGLE_START, _ANGLE_END)
    ctx.fill()
    ctx.closePath()


def draw_text(ctx: CanvasRenderingContext2D, text: str, position: tuple[int, int], font: str, fill_style: str) -> None:
    """テキストの描画."""
    (x, y) = position
    text = text
    ctx.font = font
    ctx.fillStyle = fill_style
    ctx.fillText(text, x, y)


class ResultView:
    """結果表示ビュー."""

    def __init__(self, model: GameModel, ctx: CanvasRenderingContext2D):
        self._model = model
        self._ctx = ctx

    def draw(self) -> None:
        """描画."""
        if self._model.is_waitstart():
            text = 'Press MouseLeft to Start'
            font = '28px bold sans-serif'
            draw_text(self._ctx,
                      text, position=(37, 182), font=font, fill_style='rgb(0, 0, 0)')
            draw_text(self._ctx,
                      text, position=(35, 180), font=font, fill_style='rgb(255, 255, 255)')
        elif self._model.is_gameover():
            text = 'GameOver !'
            font = '60px bold sans-serif'
            draw_text(self._ctx,
                      text, position=(37, 202), font=font, fill_style='rgb(0, 0, 0)')
            draw_text(self._ctx,
                      text, position=(35, 200), font=font, fill_style='rgb(255, 0, 0)')
        elif self._model.is_success():
            text = 'Success !'
            font = '60px bold sans-serif'
            draw_text(self._ctx,
                      text, position=(57, 202), font=font, fill_style='rgb(0, 0, 0)')
            draw_text(self._ctx,
                      text, position=(55, 200), font=font, fill_style='rgb(0, 255, 255)')


class NextStoneView:
    """次の石ビュー."""

    def __init__(self, model: GameModel, ctx: CanvasRenderingContext2D):
        self._model = model
        self._ctx = ctx

    def draw(self) -> None:
        """描画."""

        # テキスト
        draw_text(self._ctx,
                  'Next', position=(440, 80), font='30px bold sans-serif', fill_style="rgb(0, 0, 0)")

        # 石
        center = (535, 70)
        draw_stone(self._ctx, center, self._model.next_stone)


class TimerView:
    """経過時間ビュー."""

    def __init__(self, model: GameModel, ctx: CanvasRenderingContext2D):
        self._model = model
        self._ctx = ctx

    def draw(self) -> None:
        """描画."""
        draw_text(self._ctx,
                  f'Time:{self._model.time_sec}', position=(440, 250), font="30px bold sans-serif", fill_style="rgb(0, 0, 0)")


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
                center = (column * cell_size + offset, row * cell_size + offset)
                draw_stone(self._ctx, center, color)


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
