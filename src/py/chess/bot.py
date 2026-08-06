from chess.chessboard import ChessBoard
from chess.helpers import Evaluation, Move
class Bot:
    def __init__(self):
        pass
    def eval(self, position: ChessBoard, depth : int, alpha : Evaluation = Evaluation(result = -1), beta : Evaluation = Evaluation(result = 1)):
        if depth < 0:
            raise ValueError("Depth must be non-negative")
        if position.checkmate():
            return Evaluation(result = 1 if(not position.whitesTurn) else -1), []
        if position.isDraw():
            return Evaluation(result = 0), []
        if depth == 0:
            return Evaluation(eval = self.heuristic(position)), []

        moves = position.possibleMoves
        best_sequence = []
        if position.whitesTurn:
            for move in moves:
                new_state = position.makeMove(move) 
                new_alpha, sequence = self.eval(new_state, depth - 1, alpha, beta)
                if(new_alpha > alpha):
                    alpha = new_alpha
                    best_sequence = [move] + sequence
                if(alpha > beta):
                    break
            return alpha.step_back(True), best_sequence
        else:
            for move in moves:
                new_state = position.makeMove(move) 
                new_beta, sequence = self.eval(new_state, depth - 1, alpha, beta)
                if(new_beta < beta):
                    beta = new_beta
                    best_sequence = [move] + sequence
                if(beta < alpha):
                    break
            return beta.step_back(False), best_sequence

    def best_move(self, position: ChessBoard, depth: int):
        if position.checkmate() or position.isDraw():
            return None
        moves = position.possibleMoves
        best_sequence = []
        if position.whitesTurn:
            alpha = Evaluation(result = -1)
            for move in moves:
                new_state = position.makeMove(move) 
                result, sequence = self.eval(new_state, depth - 1, alpha = alpha)
                if(result > alpha):
                    best_sequence = [move] + sequence 
                    alpha = result
            return alpha.step_back(True), best_sequence
        else:
            beta = Evaluation(result = 1)
            for move in moves:
                new_state = position.makeMove(move) 
                result, sequence = self.eval(new_state, depth - 1, beta = beta)
                if(result < beta):
                    best_sequence = [move] + sequence 
                    beta = result
            return beta.step_back(False), best_sequence
    @staticmethod
    def heuristic(position: ChessBoard):
        sum = 0
        for square in position.positions[0]:
            piece = position.boardState[square[0]][square[1]].lower()
            match piece:
                case "p":
                    sum += 1
                case "n":
                    sum += 3
                case "b":
                    sum += 3
                case "r":
                    sum += 5
                case "q":
                    sum += 9
                case _:
                    raise ValueError("Board positions invalid, see issue")
        for square in position.positions[1]:
            piece = position.boardState[square[0]][square[1]].lower()
            match piece:
                case "p":
                    sum -= 1
                case "n":
                    sum -= 3
                case "b":
                    sum -= 3
                case "r":
                    sum -= 5
                case "q":
                    sum -= 9
                case _:
                    raise ValueError("Board positions invalid, see issue")
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