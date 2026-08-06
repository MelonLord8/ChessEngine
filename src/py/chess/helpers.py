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
    mateWhite: bool | None
    mateIn: int | None
    eval: int | None
    result: int | None

    def __init__(self, eval : int | None = None, mateWhite: bool | None = None, mateIn: int | None = None, result: int | None = None):

        if ((mateWhite is None) != (mateIn is None)):
            raise ValueError()
        if not (not ((eval is None) != ((mateWhite is None) != (result is None))) and not((eval is None) and (mateWhite is None) and (result is None)) ): # Only one
            raise ValueError()

        self.mateIn = mateIn
        self.mateWhite = mateWhite
        self.eval = eval
        self.result = result


    def __eq__(self, other: Evaluation):
        self_effective_eval = self.eval
        other_effective_eval = other.eval
        if not (self.result is None or other.result is None):
            return self.result == other.result
        if(self_effective_eval is None and other_effective_eval is None):
            return (self.mateIn == other.mateIn) and (self.mateWhite == other.mateWhite)
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
                if(self.mateWhite and other.mateWhite):
                    return self.mateIn < other.mateIn
                if(self.mateWhite):
                    return True
                if(other.mateWhite):
                    return False 
                return self.mateIn > other.mateIn
            return self.mateWhite
        if(other_effective_eval is None):
            return not other.mateWhite
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
                if(self.mateWhite and other.mateWhite):
                    return self.mateIn > other.mateIn
                if(self.mateWhite):
                    return False
                if(other.mateWhite):
                    return True 
                return self.mateIn < other.mateIn
            return not(self.mateWhite)
        if(other_effective_eval is None):
            return other.mateWhite
        return self_effective_eval < other_effective_eval

    def __ge__(self, other: Evaluation):
        return self == other or self > other
    def __le__(self, other: Evaluation):
        return self == other or self < other
    def __ne__(self, other: Evaluation):
        return not(self == other)
    def __str__(self):
        if not(self.mateWhite is None):
            return("W" if self.mateWhite else "B") + "M" + str(self.mateIn)
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

    def step_back(self, whitesTurn: bool):
        if not (self.result is None):
            if(self.result == 1):
                return Evaluation(mateWhite = True, mateIn = 1)
            elif(self.result == -1):
                return Evaluation(mateWhite = False, mateIn = 1)
            return self
        if not(self.mateWhite is None):
            if(self.mateWhite and whitesTurn):
                return Evaluation(mateWhite = True, mateIn = self.mateIn + 1)
            elif((not self.mateWhite) and (not whitesTurn)):
                return Evaluation(mateWhite= False, mateIn = self.mateIn + 1)
        return self
            
def validSquare(square : tuple[int, int]):
    return (square[0] >= 0 and square[0] <= 7 and square[1] >= 0 and square[1] <= 7)