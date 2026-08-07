from chess.chessboard import ChessBoard
from chess.helpers import Evaluation, Move
class Bot:
    def __init__(self):
        pass
    def eval(self, position: ChessBoard, depth: int, alpha: Evaluation = Evaluation(result=-1), beta: Evaluation = Evaluation(result=1)):
        if depth < 0:
            raise ValueError("Depth must be non-negative")
        if position.checkmate():
            return Evaluation(result=-1), []
        if position.isDraw():
            return Evaluation(result=0), []
        if depth == 0:
            return Evaluation(eval=self.heuristic(position, position.whitesTurn)), []

        best_seq = []
        for move in position.possibleMoves:
            new_state = position.makeMove(move)
            score, sequence = self.eval(new_state, depth - 1, -beta, -alpha)
            score = score.step_back()
            if(move.oldSquare == (5, 0) and move.newSquare == (7, 0)):
                print(move, score, depth, sequence)
            if score > alpha:
                alpha = score
                best_seq = [move] + sequence

            if alpha > beta:
                break

        return alpha, best_seq
    @staticmethod
    def heuristic(position: ChessBoard, whitesTurn: bool):
        sign = 1 if whitesTurn else -1
        sum = 0

        for square in position.positions[0]:
            piece = position.boardState[square[0]][square[1]].lower()
            match piece:
                case "p": sum += sign * 1
                case "n": sum += sign * 3
                case "b": sum += sign * 3
                case "r": sum += sign * 5
                case "q": sum += sign * 9
                case _: raise ValueError("Board positions invalid, see issue")

        for square in position.positions[1]:
            piece = position.boardState[square[0]][square[1]].lower()
            match piece:
                case "p": sum -= sign * 1
                case "n": sum -= sign * 3
                case "b": sum -= sign * 3
                case "r": sum -= sign * 5
                case "q": sum -= sign * 9
                case _: raise ValueError("Board positions invalid, see issue")

        return sum

    def countPositions(self, position: ChessBoard, depth: int, display = False):
        if(depth == 1):
            return len(position.possibleMoves)
        if(position.checkmate() or position.isDraw()):
            return 1
        out = 0

        for move in position.possibleMoves:
            new_positions = self.countPositions(position.makeMove(move), depth - 1)
            out += new_positions
            if(display):
                print(move, new_positions)
        return out