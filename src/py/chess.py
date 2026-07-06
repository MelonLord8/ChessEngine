knight_permutations = [(1, 2), (1, -2), (-1, -2), (-1, 2), (2, 1), (2, -1), (-2, -1), (-2, 1)]
kingPermutations = [(1, 1), (1, 0), (0, 1), (0, -1), (1, -1), (-1, -1), (-1, 1), (-1, 0)]
class Move:
    piece: str 
    castleType: str | None
    oldSquare: tuple[int, int]
    newSquare: tuple[int, int]
    promotion: str | None

    def __init__(self, piece: str, oldSquare: tuple[int, int] = None, newSquare : tuple[int, int] = None, castleType : str | None = None, promotion : str | None = None ):
        try:
            if piece is None:
                raise ValueError()
            if piece.lower() != "p" and not(promotion is None):
                raise ValueError()
            if piece.lower() != "k" and not(castleType is None):
                raise ValueError()
            if not (castleType is None):
                if(not (castleType in ['k', 'q', "K", "Q"] and oldSquare is None and newSquare is None and promotion is None)):
                    raise ValueError()
                if(not (ChessBoard.validSquare(oldSquare) and ChessBoard.validSquare(newSquare) and oldSquare != newSquare)):
                    raise ValueError()
                if(not promotion is None):
                    if not((newSquare[1] == 7 and promotion in ["N", "Q", "R", "B"]) or (newSquare[1] == 0 and promotion in ["n", "q", "r", "b"])):
                        raise ValueError()
                        
        except:
            raise ValueError("Parameters isCastle: {isCastle}, castleType: {castleType}, old_square: {old_square}, new_square {new_square}, promotion {promotion} is invalid")
        self.piece = piece
        self.castleType = castleType
        self.oldSquare = oldSquare
        self.newSquare = newSquare
        self.promotion = promotion

    def __str__(self):
        return f"( {self.piece}, {self.oldSquare}, {self.newSquare}, {self.castleType}, {self.promotion} )"
    def __repr__(self):
        return self.__str__()
class ChessBoard:
    def __init__(self):
        self.boardState : list[str] = ["RNBQKBNR", "PPPPPPPP", "--------", "--------", "--------", "--------", "pppppppp", "rnbqkbnr"]
        self.whitesTurn = True
        #KQkq
        self.castling = [True, True, True, True]
        self.enPassant = None 
        self.moveNumber = 1
        self.halfMoves = 0
        self.check = None
        self.kings : list[tuple[int, int]] = [(0, 4), (7, 4)]
        self.positions :  list[tuple[int, int]] = [(i, j) for i in [0, 1, 6, 7] for j in range(8)]
        self.positions.remove((0, 4))
        self.positions.remove((7, 4))
        self.possibleMoves : list[Move] = self.exploreMoves(self.whitesTurn)

    @staticmethod
    def validSquare(square : tuple[int, int]):
        return (square[0] >= 0 and square[0] <= 7 and square[1] >= 0 and square[1] <= 7)

    @staticmethod
    def boardStateInCheck(boardState: list[str], white: bool, square: tuple[int, int]):
        if not ChessBoard.validSquare(square):
            raise ValueError()
        # Straight Lines
        for i in range(1, square[1] + 1):
            
            piece = boardState[square[0]][square[1] - i]
            if(piece == "-" or (piece == "k" and not white) or (piece == "K" and white)):
                continue
            if((piece == "q" and white) or (piece == "r" and white) or (piece == "Q" and not white) or (piece == "R" and not white)):
                return True
            if((piece == "k" and white) or (piece == "K" and not white)) and i == 1:
                return True
            else:
                break
        for i in range(1, 8 - square[1]):
            piece = boardState[square[0]][square[1] + i]
            if(piece == "-" or (piece == "k" and not white) or (piece == "K" and white)):
                continue
            if((piece == "q" and white) or (piece == "r" and white) or (piece == "Q" and not white) or (piece == "R" and not white)):
                return True
            if((piece == "k" and white) or (piece == "K" and not white)) and i == 1:
                return True
            else:
                break

        for i in range(1, square[0] + 1):
            piece = boardState[square[0] - i][square[1]]
            if(piece == "-" or (piece == "k" and not white) or (piece == "K" and white)):
                continue
            if((piece == "q" and white) or (piece == "r" and white) or (piece == "Q" and not white) or (piece == "R" and not white)):
                return True
            if((piece == "k" and white) or (piece == "K" and not white)) and i == 1:
                return True
            else:
                break

        for i in range(1, 8 - square[0]):
            piece = boardState[square[0] + i][square[1]]
            if(piece == "-" or (piece == "k" and not white) or (piece == "K" and white)):
                continue
            if((piece == "q" and white) or (piece == "r" and white) or (piece == "Q" and not white) or (piece == "R" and not white)):
                return True
            if((piece == "k" and white) or (piece == "K" and not white)) and i == 1:
                return True
            else:
                break
        
        #Diagonals
        for i in range(1, min(square[0], square[1]) + 1):
            piece = boardState[square[0] - i][square[1] - i]
            if(piece == "-" or (piece == "k" and not white) or (piece == "K" and white)):
                continue
            if((piece == "q" and white) or (piece == "b" and white) or (piece == "Q" and not white) or (piece == "B" and not white)):
                return True
            if((piece == "k" and white) or (piece == "K" and not white) or (piece == "p" and white)) and i == 1:
                return True
            else:
                break
        for i in range(1, min(7 - square[0], 7 - square[1]) + 1):
            piece = boardState[square[0] + i][square[1] + i]
            if(piece == "-" or (piece == "k" and not white) or (piece == "K" and white)):
                continue
            if((piece == "q" and white) or (piece == "b" and white) or (piece == "Q" and not white) or (piece == "B" and not white)):
                return True
            if((piece == "k" and white) or (piece == "K" and not white) or (piece == "P" and not white)) and i == 1:
                return True
            else:
                break
        for i in range(1, min(square[0], 7 - square[1]) + 1):
            piece = boardState[square[0] - i][square[1] + i]
            if(piece == "-" or (piece == "k" and not white) or (piece == "K" and white)):
                continue
            if((piece == "q" and white) or (piece == "b" and white) or (piece == "Q" and not white) or (piece == "B" and not white)):
                return True
            if((piece == "k" and white) or (piece == "K" and not white) or (piece == "P" and not white)) and i == 1:
                return True
            else:
                break
        for i in range(1, min( 7 - square[0], square[1]) + 1):
            piece = boardState[square[0] + i][square[1] - i]
            if(piece == "-" or (piece == "k" and not white) or (piece == "K" and white)):
                continue
            if((piece == "q" and white) or (piece == "b" and white) or (piece == "Q" and not white) or (piece == "B" and not white)):
                return True
            if((piece == "k" and white) or (piece == "K" and not white) or (piece == "p" and white)) and i == 1:
                return True
            else:
                break
        
        for permutation in knight_permutations:
            new_square = (square[0] + permutation[0], square[1] + permutation[1])
            if(ChessBoard.validSquare(new_square)):
                piece = boardState[new_square[0]][new_square[1]]
                if (piece == "n" and white) or (piece == "N" and not white):
                    return True
        return False
    
    def inCheck(self, white: bool, square: tuple[int, int]):
        if(not self.validSquare(square)):
            raise ValueError()
        return self.boardStateInCheck(self.boardState, white, square)
    def kingInCheck(self):
        if self.check is None:
            self.check = ChessBoard.boardStateInCheck(self.boardState, self.whitesTurn, self.kings[not self.whitesTurn])
        return self.check
    @staticmethod
    def validMove(move: Move, state: list[str], white: bool, kingSquare: tuple[int, int]):
        """
            Sees if a move goes over your own piece, or if it leads to your king being in check
            Not yet meant to validate king moves as that is a bit tricky, might handle later
        """
        if(not ChessBoard.validSquare(kingSquare)):
            raise ValueError()
        existingPiece = state[move.newSquare[0]][move.newSquare[1]]
        if ((existingPiece.lower() == existingPiece) != white and existingPiece != "-"):
            return False

        piece = state[move.oldSquare[0]][move.oldSquare[1]]

        state[move.newSquare[0]] = state[move.newSquare[0]][:move.newSquare[1]] + piece + state[move.newSquare[0]][move.newSquare[1] + 1:]
        state[move.oldSquare[0]] = state[move.oldSquare[0]][:move.oldSquare[1]] + '-' + state[move.oldSquare[0]][move.newSquare[1] + 1:]
        return not ChessBoard.boardStateInCheck(state, white, kingSquare)

    def exploreMoves(self, white = None):
        out : list[tuple[tuple[int, int], tuple[int, int], str]] = []
        if white is None:
            white = self.whitesTurn
        kingSquare = self.kings[not white]
        piece = self.boardState[kingSquare[0]][kingSquare[1]]
        for perm in kingPermutations:
            tempState = self.boardState.copy()
            newSquare = (kingSquare[0] + perm[0], kingSquare[1] + perm[1])
            if(not ChessBoard.validSquare(newSquare)):
                continue
            existingPiece = self.boardState[newSquare[0]][newSquare[1]]
            if (existingPiece.lower() == existingPiece) != white and existingPiece != "-":
                continue
            tempState[newSquare[0]] = tempState[newSquare[0]][:newSquare[1]] + piece + tempState[newSquare[0]][newSquare[1] + 1:]
            tempState[kingSquare[0]] = tempState[kingSquare[0]][:kingSquare[1]] + '-' + tempState[kingSquare[0]][kingSquare[1] + 1:]

            if(not ChessBoard.boardStateInCheck(tempState, white, newSquare)):
                out.append(Move(piece, kingSquare, newSquare))
                
        if(not self.kingInCheck()):
            kingSideCastle = self.castling[(not white)]
            for i in range(5, 7):
                if (not kingSideCastle): break
                kingSideCastle = kingSideCastle and (self.boardState[7 * (not white)][i] == "-")
                
            for i in range(5, 7):
                if (not kingSideCastle): break
                kingSideCastle = kingSideCastle and (self.inCheck(white, (7 * (not white),i)))

            if(kingSideCastle):
                out.append(Move(piece, None, None, True, "K" if white else "k"))

            queenSideCastle = self.castling[(not white + 1)]
            for i in range(1, 4):
                if (not queenSideCastle): break
                queenSideCastle = queenSideCastle and (self.boardState[7 * (not white)][i] == "-")
                
            for i in range(1, 4):
                if (not queenSideCastle): break
                queenSideCastle = queenSideCastle and (self.inCheck(white, (7 * (not white),i)))
            if(queenSideCastle):
                out.append(Move(piece, None, None, True, "Q" if white else "q"))
            

        for square in self.positions:
            piece = self.boardState[square[0]][square[1]] 
            if((piece == piece.lower()) == white):
                continue
            pieceType = piece.lower()
            if pieceType in ["k", "-"]:
                continue
            if piece == "P":
                if self.boardState[square[0] + 1][square[1]] == "-" :
                    move = Move(piece, square, (square[0] + 1, square[1]), None, None)
                    if(ChessBoard.validMove(move, self.boardState.copy(), white, kingSquare)):
                        if(square[0] == 6):
                            for promType in ["Q", "N", "B", "R"]:
                                out.append(Move(square, (square[0] + 1, square[1]), None, promType))
                        else:
                            out.append(move)
                    if square[0] == 1 and self.boardState[square[0] + 2][square[1]] == "-":
                        move = Move(piece, square, (square[0] + 2, square[1]), None, None)
                        if(ChessBoard.validMove(move, self.boardState.copy(), white, kingSquare)):
                            out.append(move)
            elif piece == "p":
                if self.boardState[square[0] - 1][square[1]] == "-" :
                    move = Move(piece, square, (square[0] - 1, square[1]), None, None)
                    if(ChessBoard.validMove(move, self.boardState.copy(), white, kingSquare)):
                        if(square[0] == 1):
                            for promType in ["q", "n", "b" "r"]:
                                out.append(Move(square, (square[0] - 1, square[1]), None, promType))
                        else:
                            out.append(Move(square, (square[0] - 1, square[1]), None, None))
                    if square[0] == 6 and self.boardState[square[0] - 2][square[1]] == "-":
                        move = Move(piece, square, (square[0] - 2, square[1]), None, None)
                        if(ChessBoard.validMove(move, self.boardState.copy(), white, kingSquare)):
                            out.append(move)
            if pieceType in ["r", "q"]:
                for i in  range(1, square[1] + 1):
                    newSquare = (square[0], square[1] - i)
                    squarePiece = self.boardState[newSquare[0]][newSquare[1]]
                    move = Move(piece, square, newSquare, None, None)
                    if(squarePiece == "-" ):
                        if(ChessBoard.validMove(move, self.boardState.copy(), white, kingSquare)):
                            out.append(move)
                        continue
                    elif((squarePiece.lower() == squarePiece) == white):
                        if(ChessBoard.validMove(move, self.boardState.copy(), white, kingSquare)):
                            out.append(move)
                    break
                for i in range(1, 8 - square[1]):
                    newSquare = (square[0], square[1] + i)
                    squarePiece = self.boardState[newSquare[0]][newSquare[1]]
                    move = Move(piece, square, newSquare, None, None)
                    if(squarePiece == "-" ):
                        if(ChessBoard.validMove(move, self.boardState.copy(), white, kingSquare)):
                            out.append(move)
                        continue
                    elif((squarePiece.lower() == squarePiece) == white):
                        if(ChessBoard.validMove(move, self.boardState.copy(), white, kingSquare)):
                            out.append(move)
                    break
                for i in range(1, square[0] + 1):
                    newSquare = (square[0] - i, square[1])
                    squarePiece = self.boardState[newSquare[0]][newSquare[1]]
                    move = Move(piece, square, newSquare, None, None)
                    if(squarePiece == "-" ):
                        if(ChessBoard.validMove(move, self.boardState.copy(), white, kingSquare)):
                            out.append(move)
                        continue
                    elif((squarePiece.lower() == squarePiece) == white):
                        if(ChessBoard.validMove(move, self.boardState.copy(), white, kingSquare)):
                            out.append(move)
                    break
                for i in  range(1, 8 - square[0]):
                    newSquare = (square[0] + i, square[1])
                    squarePiece = self.boardState[newSquare[0]][newSquare[1]]
                    move = Move(piece, square, newSquare, None, None)
                    if(squarePiece == "-" ):
                        if(ChessBoard.validMove(move, self.boardState.copy(), white, kingSquare)):
                            out.append(move)
                        continue
                    elif((squarePiece.lower() == squarePiece) == white):
                        if(ChessBoard.validMove(move, self.boardState.copy(), white, kingSquare)):
                            out.append(move)
                    break
            if pieceType in ["b", "q"]:
                for i in range(1, min(square[0], square[1]) + 1):
                    newSquare = (square[0] - i, square[1] - i)
                    squarePiece = self.boardState[newSquare[0]][newSquare[1]]
                    move = Move(piece, square, newSquare, None, None)
                    if(squarePiece == "-" ):
                        if(ChessBoard.validMove(move, self.boardState.copy(), white, kingSquare)):
                            out.append(move)
                        continue
                    elif((squarePiece.lower() == squarePiece) == white):
                        if(ChessBoard.validMove(move, self.boardState.copy(), white, kingSquare)):
                            out.append(move)
                    break
                for i in range(1, min(7 - square[0], 7 - square[1]) + 1):
                    newSquare = (square[0] + i, square[1] + i)
                    squarePiece = self.boardState[newSquare[0]][newSquare[1]]
                    move = Move(piece, square, newSquare, None, None)
                    if(squarePiece == "-" ):
                        if(ChessBoard.validMove(move, self.boardState.copy(), white, kingSquare)):
                            out.append(move)
                        continue
                    elif((squarePiece.lower() == squarePiece) == white):
                        if(ChessBoard.validMove(move, self.boardState.copy(), white, kingSquare)):
                            out.append(move)
                    break           
                for i in range(1, min(square[0], 7 - square[1]) + 1):
                    newSquare = (square[0] - i, square[1] + i)
                    squarePiece = self.boardState[newSquare[0]][newSquare[1]]
                    move = Move(piece, square, newSquare, None, None)
                    if(squarePiece == "-" ):
                        if(ChessBoard.validMove(move, self.boardState.copy(), white, kingSquare)):
                            out.append(move)
                        continue
                    elif((squarePiece.lower() == squarePiece) == white):
                        if(ChessBoard.validMove(move, self.boardState.copy(), white, kingSquare)):
                            out.append(move)
                    break
                for i in range(1, min(7 - square[0], square[1]) + 1):
                    newSquare = (square[0] + i, square[1] - i)
                    squarePiece = self.boardState[newSquare[0]][newSquare[1]]
                    move = Move(piece, square, newSquare, None, None)
                    if(squarePiece == "-" ):
                        if(ChessBoard.validMove(move, self.boardState.copy(), white, kingSquare)):
                            out.append(move)
                        continue
                    elif((squarePiece.lower() == squarePiece) == white):
                        if(ChessBoard.validMove(move, self.boardState.copy(), white, kingSquare)):
                            out.append(move)
                    break  
            if pieceType == "n":
                for permutation in knight_permutations:
                    newSquare = (square[0] + permutation[0], square[1] + permutation[1])
                    if(not ChessBoard.validSquare(newSquare)):
                        continue
                    move = Move(piece, square, newSquare, None, None)
                    if(ChessBoard.validMove(move, self.boardState.copy(), white, kingSquare)):
                        print(self.boardState)
                        out.append(move)
        return out
            