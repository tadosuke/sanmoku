import pygame

import input
from ban import Ban
from game import GameModel
from values import Cell, Position, StoneColor

#: 石の色
_STONE_COLORS = {
    StoneColor.Red: (200, 0, 0),
    StoneColor.Green: (0, 200, 0),
    StoneColor.Blue: (0, 0, 200),
    StoneColor.Yellow: (200, 200, 0),
}


class ResultView:
    """結果表示ビュー."""

    def __init__(self, model: GameModel, screen: pygame.Surface):
        self._model = model
        self._screen = screen

    def draw(self) -> None:
        """描画."""
        if self._model.is_waitstart():
            font = pygame.font.SysFont("メイリオ", 40)
            mes = "Press MouseLeft to Start"
            text = font.render(mes, True, (0, 0, 0))
            self._screen.blit(text, [37, 172])
            text = font.render(mes, True, (255, 255, 255))
            self._screen.blit(text, [35, 170])
        elif self._model.is_gameover():
            font = pygame.font.SysFont("メイリオ", 80)
            mes = "GameOver !"
            text = font.render(mes, True, (0, 0, 0))
            self._screen.blit(text, [42, 152])
            text = font.render(mes, True, (255, 0, 0))
            self._screen.blit(text, [40, 150])
        elif self._model.is_success():
            font = pygame.font.SysFont("メイリオ", 80)
            mes = "Success !"
            text = font.render(mes, True, (0, 0, 0))
            self._screen.blit(text, [87, 152])
            text = font.render(mes, True, (0, 255, 255))
            self._screen.blit(text, [85, 150])


class TimerView:
    """経過時間ビュー."""

    def __init__(self, model: GameModel, screen: pygame.Surface):
        self._model = model
        self._screen = screen
        self._font = pygame.font.SysFont("メイリオ", 40)

    def draw(self) -> None:
        """描画."""

        # テキスト
        text = self._font.render(f'Time:{self._model.time_sec}', True, (0, 0, 0))
        self._screen.blit(text, [440, 250])


class NextStoneView:
    """次の石ビュー."""

    def __init__(self, model: GameModel, screen: pygame.Surface):
        self._model = model
        self._screen = screen
        self._font = pygame.font.SysFont("メイリオ", 40)

    def draw(self) -> None:
        """描画."""
        # テキスト
        text = self._font.render("Next", True, (0, 0, 0))
        self._screen.blit(text, [440, 80])

        # 石
        radius = 15
        pos = (530, 77 + radius)
        pygame.draw.circle(self._screen, _STONE_COLORS[self._model.next_stone], pos, radius, width=0)  # type: ignore


class BanView:
    """盤用ビュー."""

    def __init__(self, ban: Ban, screen: pygame.Surface):
        if ban is None:
            raise ValueError()
        self._ban = ban
        self._screen = screen

    def draw(self) -> None:
        """描画."""
        margin = self._ban.margin
        cell_size = (self._ban.size - margin * 2) / self._ban.cell_num

        # 土台
        rect = pygame.Rect(0, 0, self._ban.size, self._ban.size)
        pygame.draw.rect(self._screen, (200, 100, 0), rect)

        # マスの枠
        line_color = (0, 0, 0)
        for x in range(self._ban.cell_num + 1):
            start_pos = (x * cell_size + margin, 0 + margin)
            end_pos = (x * cell_size + margin, self._ban.size - margin)
            pygame.draw.line(self._screen, line_color, start_pos, end_pos, width=2)
        for y in range(self._ban.cell_num + 1):
            start_pos = (margin, y * cell_size + margin)
            end_pos = (self._ban.size - margin, y * cell_size + margin)
            pygame.draw.line(self._screen, line_color, start_pos, end_pos, width=2)

        # 石
        for row in range(self._ban.cell_num):
            for column in range(self._ban.cell_num):
                color = self._ban.get(Cell(row, column))
                if color == 0:
                    continue
                offset = margin + cell_size / 2
                pos = (column * cell_size + offset, row * cell_size + offset)
                radius = 15
                pygame.draw.circle(self._screen, _STONE_COLORS[color], pos, radius, width=0)  # type: ignore


class GameView:
    """PyGame用ビュー."""

    def __init__(self, model: GameModel, scr_w: int, scr_h: int):
        if model is None:
            raise ValueError()
        self._model = model
        self._scr_w = scr_w
        self._scr_h = scr_h
        self._ban = model.ban

        pygame.init()
        self._screen: pygame.Surface = pygame.display.set_mode((scr_w, scr_h))  # type: ignore
        pygame.display.set_caption("Sanmoku")

        self._ban_view = BanView(self._ban, self._screen)
        self._next_stone_view = NextStoneView(model, self._screen)
        self._timer_view = TimerView(model, self._screen)
        self._result_view = ResultView(model, self._screen)

    def update(self) -> bool:
        self._draw()
        return self._process_event()

    def _draw(self) -> None:
        """描画."""
        self._screen.fill((255, 255, 200))
        self._ban_view.draw()
        self._next_stone_view.draw()
        self._timer_view.draw()
        self._result_view.draw()
        pygame.display.update()

    def _process_event(self) -> bool:
        """イベント処理."""
        for event in pygame.event.get():
            if self._model.enable_control():
                self._process_mouse_event()

            # 終了イベント
            if event.type == pygame.QUIT:
                pygame.quit()  # pygameのウィンドウを閉じる
                return False

        return True

    def _process_mouse_event(self):
        """マウスイベントの処理."""
        (btn1, btn2, btn3) = pygame.mouse.get_pressed()  # type: ignore
        if btn1:
            state = input.InputState.Press
        else:
            state = input.InputState.Release

        param = input.OperationParam(
            code=input.VirtualKey.MouseLeft,
            state=state,
            position=Position(*pygame.mouse.get_pos())  # type: ignore
        )
        self._model.operate(param)
