import pytest
from chess.chessboard import ChessBoard
from chess.bot import Bot
from chess.helpers import Evaluation


class TestBotMate:
    @pytest.fixture
    def bot(self):
        return Bot()

    def test_m1(self, bot: Bot):
        board = ChessBoard("6k1/8/6K1/8/8/2R5/8/8 w - - 0 1")
        result, _ = bot.eval(board, 3)
        assert result.mateIn == 1, "Should find mate in 1 for white"

    def test_m2(self, bot: Bot):
        board = ChessBoard("6K1/8/r7/8/6k1/2r5/8/8 b - - 0 1")
        result, _ = bot.eval(board, 4)
        assert result.mateIn == 2, "Should find mate in 2"

    def test_no_mate_available(self, bot: Bot):
        board = ChessBoard("rnb-kbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        result, _ = bot.eval(board, 2)
        assert result.result is None, "Should not have immediate mate"
        assert result.eval is not None, "Should have positional eval"

    def test_eval_favors_winning_position(self, bot: Bot):
        board = ChessBoard("rnb-kbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        result, _ = bot.eval(board, 2)
        assert result.eval > 0, "White should have positive eval (queen advantage)"
