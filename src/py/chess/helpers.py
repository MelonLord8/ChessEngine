class Move:
    piece: str 
    castleType: str | None
    oldSquare: tuple[int, int]
    newSquare: tuple[int, int]
    promotion: str | None
    enPassant: bool
    isDirectCapture: bool

    def __init__(self, piece: str, oldSquare: tuple[int, int] = None, newSquare : tuple[int, int] = None, castleType : str | None = None, promotion : str | None = None, enPassant: bool = False, isDirectCapture : bool = False):
        try:
            if castleType is None:
                if piece is None: # Only one can be true at the same time
                    raise ValueError()
                if (piece.lower() != "p" and (not(promotion is None) or enPassant)) :
                    raise ValueError()
                if(not (validSquare(oldSquare) and validSquare(newSquare) and oldSquare != newSquare)):
                        raise ValueError()
                if(not (promotion is None)):
                    if not((newSquare[0] == 7 and promotion in ["N", "Q", "R", "B"]) or (newSquare[0] == 0 and promotion in ["n", "q", "r", "b"])):
                        raise ValueError()
                if not (castleType is None): # Only if castling
                    if(not (castleType in ['k', 'q', "K", "Q"] and oldSquare is None and newSquare is None and promotion is None)):
                        raise ValueError()
                    if(not (promotion is None)):
                        raise ValueError()
                    if (isDirectCapture):
                        raise ValueError()
            else:
                if not(piece is None):
                    raise ValueError()
        except:
            raise ValueError(f"Parameters, castleType: {castleType}, old_square: {oldSquare}, new_square {newSquare}, promotion {promotion} is invalid")
        self.piece = piece
        self.castleType = castleType
        self.oldSquare = oldSquare
        self.newSquare = newSquare
        self.promotion = promotion
        self.enPassant = enPassant
        self.isDirectCapture = isDirectCapture
    @staticmethod
    def translateSquare(square: tuple[int, int] | None):
        if square is None:
            return None
        return chr(square[1] + 97) + str(square[0] + 1)
    def __str__(self):
        return f"( {self.piece}, {self.translateSquare(self.oldSquare)}, {self.translateSquare(self.newSquare)}, {self.castleType}, {self.promotion}, {self.enPassant}, {self.isDirectCapture})"
    def __repr__(self):
        return self.__str__()

class Evaluation:
    __slots__ = ('currentWins', 'mateIn', 'eval', 'result')

    currentWins: bool | None
    mateIn: int | None
    eval: int | None
    result: int | None

    def __init__(self, eval : int | None = None, currentWins: bool | None = None, mateIn: int | None = None, result: int | None = None):

        if ((currentWins is None) != (mateIn is None)):
            raise ValueError()
        if not (not ((eval is None) != ((currentWins is None) != (result is None))) and not((eval is None) and (currentWins is None) and (result is None)) ): # Only one
            raise ValueError()

        self.mateIn = mateIn
        self.currentWins = currentWins
        self.eval = eval
        self.result = result


    def __eq__(self, other: Evaluation):
        self_effective_eval = self.eval
        other_effective_eval = other.eval
        if not (self.result is None or other.result is None):
            return self.result == other.result
        if(self_effective_eval is None and other_effective_eval is None):
            return (self.mateIn == other.mateIn) and (self.currentWins == other.currentWins)
        if self.result == 0:
            self_effective_eval = 0
        if other.result == 0:
            other_effective_eval = 0
        return self_effective_eval == other_effective_eval
    def __gt__(self, other: Evaluation):
        self_effective_eval = self.eval
        other_effective_eval = other.eval
        if (not self.result is None) and (not other.result is None):
            return self.result > other.result
        if not (self.result is None):
            if(self.result == 1):
                return True
            if(self.result == -1):
                return False
            self_effective_eval = 0
        if not other.result is None:
            if(other.result == 1):
                return False
            if(other.result == -1):
                return True
            other_effective_eval = 0
        if(self_effective_eval is None):
            if (other_effective_eval is None):
                if(self.currentWins and other.currentWins):
                    return self.mateIn < other.mateIn
                if(self.currentWins):
                    return True
                if(other.currentWins):
                    return False 
                return self.mateIn > other.mateIn
            return self.currentWins
        if(other_effective_eval is None):
            return not other.currentWins
        return self_effective_eval > other_effective_eval
    
    def __lt__(self, other: Evaluation):
        self_effective_eval = self.eval
        other_effective_eval = other.eval
        if (not self.result is None) and (not other.result is None):
            return self.result < other.result
        if not (self.result is None):
            if(self.result == 1):
                return False
            if(self.result == -1):
                return True
            self_effective_eval = 0
        if not other.result is None:
            if(other.result == 1):
                return True
            if(other.result == -1):
                return False
            other_effective_eval = 0
        if(self_effective_eval is None):
            if (other_effective_eval is None):
                if(self.currentWins and other.currentWins):
                    return self.mateIn > other.mateIn
                if(self.currentWins):
                    return False
                if(other.currentWins):
                    return True 
                return self.mateIn < other.mateIn
            return not(self.currentWins)
        if(other_effective_eval is None):
            return other.currentWins
        return self_effective_eval < other_effective_eval

    def __ge__(self, other: Evaluation):
        return self == other or self > other
    def __le__(self, other: Evaluation):
        return self == other or self < other
    def __ne__(self, other: Evaluation):
        return not(self == other)

    def __neg__(self):
        if self.result is not None:
            return Evaluation(result=-self.result)
        if self.currentWins is not None:
            return Evaluation(currentWins=not self.currentWins, mateIn=self.mateIn)
        return Evaluation(eval=-self.eval)

    def __str__(self):
        if not(self.currentWins is None):
            return("" if self.currentWins else "-") + "M" + str(self.mateIn)
        elif not(self.result is None):
            if(self.result == 1):
                return "1-0"
            elif(self.result == -1):
                return "0-1"
            elif(self.result == 0):
                return "1/2 - 1/2"
        else:
            return str(self.eval)
    def __repr__(self):
        return self.__str__()

    def step_back(self):
        if not (self.result is None):
            if(self.result == 1):
                return Evaluation(currentWins = False, mateIn = 1)
            elif(self.result == -1):
                return Evaluation(currentWins = True, mateIn = 1)
            return self
        if not(self.currentWins is None):
            if(self.currentWins):
                return Evaluation(currentWins = False, mateIn = self.mateIn)
            else:
                return Evaluation(currentWins = True, mateIn = self.mateIn + 1)
        return self
            
def validSquare(square : tuple[int, int]):
    return (square[0] >= 0 and square[0] <= 7 and square[1] >= 0 and square[1] <= 7)