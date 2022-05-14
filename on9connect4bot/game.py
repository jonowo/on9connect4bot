import itertools

from .constants import BLUE_EMOJI, NUMBERS_EMOJI, RED_EMOJI, WHITE_EMOJI


class Game:
    ROWS = 6
    COLS = 7

    def __init__(self, p1_id: int, p2_id: int, board: list[list[int]]) -> None:
        self.player_ids = [p1_id, p2_id]
        self.board = board
        self.turn = (Game.ROWS * Game.COLS - tuple(itertools.chain(*board)).count(0)) % 2

    def __str__(self) -> str:
        emojis = [WHITE_EMOJI, BLUE_EMOJI, RED_EMOJI]
        text = [[""] * Game.COLS for _ in range(Game.ROWS)]
        for i in range(Game.ROWS):
            for j in range(Game.COLS):
                text[i][j] = emojis[self.board[i][j]]
        return "\n".join(["".join(row) for row in text] + [NUMBERS_EMOJI])

    def make_move(self, col: int) -> None:
        for row in range(Game.ROWS - 1, -1, -1):
            if self.board[row][col] == 0:
                self.board[row][col] = self.turn + 1
                return
        raise ValueError

    def is_win(self, pos_list: list[tuple[int, int]]) -> bool:
        return all(self.board[i][j] == self.turn + 1 for i, j in pos_list)

    def check_result(self) -> int:
        """
        -1: Game unfinished
        0: Draw
        1: Current player wins
        """
        for i in range(Game.ROWS):
            for j in range(Game.COLS):
                # Vertical
                if i + 3 < Game.ROWS:
                    if self.is_win([(i, j), (i + 1, j), (i + 2, j), (i + 3, j)]):
                        return 1

                # Horizontal
                if j + 3 < Game.COLS:
                    if self.is_win([(i, j), (i, j + 1), (i, j + 2), (i, j + 3)]):
                        return 1

                # Diagonal with -ve slope
                if i + 3 < Game.ROWS and j + 3 < Game.COLS:
                    if self.is_win([(i, j), (i + 1, j + 1), (i + 2, j + 2), (i + 3, j + 3)]):
                        return 1

                # Diagonal with +ve slope
                if i >= 3 and j + 3 < Game.COLS:
                    if self.is_win([(i, j), (i - 1, j + 1), (i - 2, j + 2), (i - 3, j + 3)]):
                        return 1

        if tuple(itertools.chain(*self.board)).count(0):
            return -1
        else:
            return 0

    def encode(self) -> str:
        rows = [0] * Game.COLS
        for i in range(Game.ROWS):
            base = 1
            for j in range(7):
                rows[i] += self.board[i][j] * base
                base *= 3

        state = ",".join(str(i) for i in rows)
        return f"{self.player_ids[0]}:{self.player_ids[1]}:{state}"

    @classmethod
    def decode_from(cls, data) -> "Game":
        p1_id, p2_id, state = data.split(":")

        rows = [int(i) for i in state.split(",")]
        board = [[0] * Game.COLS for _ in range(Game.ROWS)]
        for i in range(Game.ROWS):
            for j in range(Game.COLS):
                board[i][j] = rows[i] % 3
                rows[i] //= 3

        return cls(int(p1_id), int(p2_id), board)

    @classmethod
    def create(cls, p1_id: int, p2_id: int) -> "Game":
        board = [[0] * Game.COLS for _ in range(Game.ROWS)]
        return cls(p1_id, p2_id, board)
