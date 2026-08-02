knight_permutations = [(1, 2), (1, -2), (-1, -2), (-1, 2), (2, 1), (2, -1), (-2, -1), (-2, 1)]
kingPermutations = [(1, 1), (1, 0), (0, 1), (0, -1), (1, -1), (-1, -1), (-1, 1), (-1, 0)]
RESET = "\x1b[0m"
PURPLE = "\x1b[38;2;0;0;0;48;5;99m"
WHITE = "\x1b[30;107m"        
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
                if(not (ChessBoard.validSquare(oldSquare) and ChessBoard.validSquare(newSquare) and oldSquare != newSquare)):
                        raise ValueError()
                if(not (promotion is None)):
                    if not((newSquare[1] == 7 and promotion in ["N", "Q", "R", "B"]) or (newSquare[1] == 0 and promotion in ["n", "q", "r", "b"])):
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
    def __str__(self):
        return f"( {self.piece}, {self.oldSquare}, {self.newSquare}, {self.castleType}, {self.promotion}, {self.enPassant})"
    def __repr__(self):
        return self.__str__()
class ChessBoard:
    
    def __init__(self, fen_string: str = None):
        if fen_string is None:
            fen_string = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        fen_arr = fen_string.split(" ")
        fenBoardState = fen_arr[0].split("/")
        fenBoardState.reverse()
        self.boardState : list[str] = []
        self.check = None
        for row in fenBoardState:
            new_row = ""
            for chr in row:
                if str.isnumeric(chr):
                    new_row += "-"*int(chr)
                else:
                    new_row += chr
            self.boardState.append(new_row)
        self.whitesTurn : bool = fen_arr[1] == "w"
        castleString = fen_arr[2]
        self.castling : list[str] = ["K" in castleString, "Q" in castleString, "k" in castleString, "q" in castleString]
        self.enPassant : int | None = None if fen_arr[3] == "-" else ord(fen_arr[3][0]) - 97
        self.moveNumber : int = int(fen_arr[5])
        self.halfMoves : int= int(fen_arr[4])
        self.kings : list[tuple[int, int]]= [(-1, -1), (-1, -1)]
        self.positions : list[list[tuple[int, int]]] = [[],[]]
        for i in range(8):
            for j in range(8):
                square: str = self.boardState[i][j]
                if(square == "-"):
                    continue
                elif(square == "k"):
                    self.kings[1] = (i, j)
                elif(square == "K"):
                    self.kings[0] = (i, j)
                else:
                    self.positions[square.lower() == square].append((i,j))
        self.possibleMoves = self.exploreMoves()
        self.threeMoveString = ''.join(self.boardState) + castleString + ("w" if self.whitesTurn else "b")
        self.threeMoveDict = {}
    def print(self, flip: bool = False):
        if not flip:
            for i in range(7, -1, -1):
                for j in range(8):
                    colour = PURPLE if ((i + j) % 2 == 0) else WHITE
                    print(colour, end = "")
                    piece = self.boardState[i][j]
                    piece_print = self.getPieceUnicode(piece)
                    if piece == "-":
                        print("  ", end = "")
                    else:
                        print(piece_print, end = "")
                print(RESET)
        else:
            for i in range(8):
                for j in range(7, -1, -1):
                    colour = PURPLE if ((i + j) % 2) == 0 else WHITE
                    print(colour , end = "")
                    piece = self.boardState[i][j]
                    piece_print = self.getPieceUnicode(piece)
                    if piece == "-":
                        print("  ", end = "")
                    else:
                        print(piece_print, end = "")
                print(RESET)

    @staticmethod
    def getPieceUnicode(piece: str):
        match piece:
            case "K":
                return "♔ "
            case "k":
                return "♚ "
            case "P":
                return "♙ "
            case "p":
                return "♟︎ "
            case "Q":
                return "♕ "
            case "q":
                return "♛ "
            case "N":
                return "♘ "
            case "n":
                return "♞ "
            case "R":
                return "♖ "
            case "r":
                return "♜ "
            case "B":
                return "♗ "
            case "b":
                return "♝ "
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
        state[move.oldSquare[0]] = state[move.oldSquare[0]][:move.oldSquare[1]] + '-' + state[move.oldSquare[0]][move.oldSquare[1] + 1:]
        if(move.enPassant):
            state[move.oldSquare[0]] = state[move.oldSquare[0]][:move.newSquare[1]] + '-' + state[move.oldSquare[0]][move.newSquare[1] + 1:]
        return not ChessBoard.boardStateInCheck(state, white, kingSquare)

    def exploreMoves(self):
        out : list[tuple[tuple[int, int], tuple[int, int], str]] = []
        white = self.whitesTurn
        kingSquare = self.kings[not white]
        piece = self.boardState[kingSquare[0]][kingSquare[1]]
        for perm in kingPermutations:
            tempState = self.boardState.copy()
            newSquare = (kingSquare[0] + perm[0], kingSquare[1] + perm[1])
            if(not ChessBoard.validSquare(newSquare)):
                continue
            existingPiece = self.boardState[newSquare[0]][newSquare[1]]
            if ((existingPiece.lower() == existingPiece) != white) and existingPiece != "-":
                continue
            isCapture = existingPiece != "-"
            tempState[newSquare[0]] = tempState[newSquare[0]][:newSquare[1]] + piece + tempState[newSquare[0]][newSquare[1] + 1:]
            tempState[kingSquare[0]] = tempState[kingSquare[0]][:kingSquare[1]] + '-' + tempState[kingSquare[0]][kingSquare[1] + 1:]

            if(not ChessBoard.boardStateInCheck(tempState, white, newSquare)):
                out.append(Move(piece, kingSquare, newSquare, isDirectCapture= isCapture))
                
        if(not self.kingInCheck()):
            kingSideCastle = self.castling[2*(not white)]
            for i in range(5, 7):
                if (not kingSideCastle): break
                kingSideCastle = kingSideCastle and (self.boardState[7 * (not white)][i] == "-")
                
            for i in range(5, 7):
                if (not kingSideCastle): break
                kingSideCastle = kingSideCastle and not(self.inCheck(white, (7 * (not white),i)))

            if(kingSideCastle):
                out.append(Move(None, castleType= "K" if white else "k"))

            queenSideCastle = self.castling[2*(not white) + 1]
            for i in range(1, 4):
                if (not queenSideCastle): break
                queenSideCastle = queenSideCastle and (self.boardState[7 * (not white)][i] == "-")
                
            for i in range(2, 4):
                if (not queenSideCastle): break
                queenSideCastle = queenSideCastle and not(self.inCheck(white, (7 * (not white),i)))
            if(queenSideCastle):
                out.append(Move(None, castleType= "Q" if white else "q"))
            

        for square in self.positions[not white]:
            piece = self.boardState[square[0]][square[1]] 
            if((piece == piece.lower()) == white):
                continue
            pieceType = piece.lower()
            if pieceType in ["k", "-"]:
                continue
            if piece == "P":
                if ChessBoard.validSquare((square[0] + 1, square[1] + 1)):  # For captures
                    existingPiece = self.boardState[square[0] + 1][square[1] + 1]
                    if (existingPiece != "-" and existingPiece.lower() == existingPiece):
                        move = Move(piece, square, (square[0] + 1, square[1] + 1), None, None, isDirectCapture=True)
                        if(ChessBoard.validMove(move, self.boardState.copy(), white, kingSquare)):
                            if(square[0] == 6):
                                for promType in ["Q", "N", "B", "R"]:
                                    out.append(Move(square, (square[0] + 1, square[1] + 1), None, promType, isDirectCapture = True))
                            else:
                                out.append(move)
                if ChessBoard.validSquare((square[0] + 1, square[1] - 1)):
                    existingPiece = self.boardState[square[0] + 1][square[1] - 1]
                    if (existingPiece != "-" and existingPiece.lower() == existingPiece):
                        move = Move(piece, square, (square[0] + 1, square[1] - 1), None, None, isDirectCapture = True)
                        if(ChessBoard.validMove(move, self.boardState.copy(), white, kingSquare)):
                            if(square[0] == 6):
                                for promType in ["Q", "N", "B", "R"]:
                                    out.append(Move(square, (square[0] + 1, square[1] - 1), None, promType, isDirectCapture = True))
                            else:
                                out.append(move)
                if self.boardState[square[0] + 1][square[1]] == "-" :
                    move = Move(piece, square, (square[0] + 1, square[1]), None, None)
                    if(ChessBoard.validMove(move, self.boardState.copy(), white, kingSquare)):  # Normal one square moves
                        if(square[0] == 6): # In case of promotion
                            for promType in ["Q", "N", "B", "R"]:
                                out.append(Move(square, (square[0] + 1, square[1]), None, promType))
                        else:
                            out.append(move)
                    if square[0] == 1 and self.boardState[square[0] + 2][square[1]] == "-": # Double step
                        move = Move(piece, square, (square[0] + 2, square[1]), None, None)
                        if(ChessBoard.validMove(move, self.boardState.copy(), white, kingSquare)):
                            out.append(move)
                    elif square[0] == 4 and not(self.enPassant is None) and abs(self.enPassant - square[1]) == 1: # En passant
                        move = Move(piece, square, (square[0] + 1, self.enPassant), enPassant= True)
                        if(ChessBoard.validMove(move, self.boardState.copy(), white, kingSquare)):
                            out.append(move)
                    
            elif piece == "p":
                if ChessBoard.validSquare((square[0] - 1, square[1] + 1)):  # For captures
                    existingPiece = self.boardState[square[0] - 1][square[1] + 1]
                    if (existingPiece != "-" and existingPiece.lower() == existingPiece):
                        move = Move(piece, square, (square[0] - 1, square[1] + 1), None, None, isDirectCapture=True)
                        if(ChessBoard.validMove(move, self.boardState.copy(), white, kingSquare)):
                            if(square[0] == 6):
                                for promType in ["q", "n", "b", "r"]:
                                    out.append(Move(square, (square[0] - 1, square[1] + 1), None, promType, isDirectCapture = True))
                            else:
                                out.append(move)
                if ChessBoard.validSquare((square[0] - 1, square[1] - 1)):
                    existingPiece = self.boardState[square[0] - 1][square[1] - 1]
                    if (existingPiece != "-" and existingPiece.lower() == existingPiece):
                        move = Move(piece, square, (square[0] - 1, square[1] - 1), None, None, isDirectCapture=True)
                        if(ChessBoard.validMove(move, self.boardState.copy(), white, kingSquare)):
                            if(square[0] == 6):
                                for promType in ["q", "n", "b", "r"]:
                                    out.append(Move(square, (square[0] - 1, square[1] - 1), None, promType, isDirectCapture = True))
                            else:
                                out.append(move)
                if self.boardState[square[0] - 1][square[1]] == "-" :
                    move = Move(piece, square, (square[0] - 1, square[1]), None, None)
                    if(ChessBoard.validMove(move, self.boardState.copy(), white, kingSquare)):
                        if(square[0] == 1):
                            for promType in ["q", "n", "b" "r"]:
                                out.append(Move(square, (square[0] - 1, square[1]), None, promType))
                        else:
                            out.append(Move(piece, square, (square[0] - 1, square[1]), None, None))
                    if square[0] == 6 and self.boardState[square[0] - 2][square[1]] == "-":
                        move = Move(piece, square, (square[0] - 2, square[1]), None, None)
                        if(ChessBoard.validMove(move, self.boardState.copy(), white, kingSquare)):
                            out.append(move)
                    elif square[0] == 3 and not(self.enPassant is None) and abs(self.enPassant - square[1]) == 1:
                        move = Move(piece, square, (square[0] - 1, self.enPassant), enPassant= True)
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
                        if(ChessBoard.validMove(move, self.boardState.copy(), white, kingSquare,)):
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
                        move.isDirectCapture = True
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
                        move.isDirectCapture = True
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
                        move.isDirectCapture = True
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
                        move.isDirectCapture = True
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
                        move.isDirectCapture = True
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
                        move.isDirectCapture = True
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
                        move.isDirectCapture = True
                        if(ChessBoard.validMove(move, self.boardState.copy(), white, kingSquare)):
                            out.append(move)
                    break  
            if pieceType == "n":
                for permutation in knight_permutations:
                    newSquare = (square[0] + permutation[0], square[1] + permutation[1])
                    if(not ChessBoard.validSquare(newSquare)):
                        continue
                    existingPiece = self.boardState[newSquare[0]][newSquare[1]]
                    if existingPiece == "-":
                        move = Move(piece, square, newSquare, None, None)
                        if(ChessBoard.validMove(move, self.boardState.copy(), white, kingSquare)):  
                            out.append(move)
                    elif (existingPiece.lower() == existingPiece) == white:
                        move = Move(piece, square, newSquare, isDirectCapture = True)
                        if(ChessBoard.validMove(move, self.boardState.copy(), white, kingSquare)):  
                            out.append(move)
                    
        return out
    def makeMove(self, move: Move) -> ChessBoard: 
        out = ChessBoard.__new__(ChessBoard)
        
        out.whitesTurn = not self.whitesTurn
        out.castling = self.castling.copy()
        out.kings = self.kings.copy()
        out.moveNumber = self.moveNumber + (not self.whitesTurn)
                  
        if move.piece == "K" and move.castleType is None:
            out.castling[0] = False
            out.castling[1] = False
        if move.piece == "k" and move.castleType is None:
            out.castling[2] = False
            out.castling[3] = False
        out.castling[0] = (out.castling[0] and (not move.oldSquare == (0,7)) and (not move.newSquare == (0,7)))
        out.castling[1] = (out.castling[1] and (not move.oldSquare == (0,0)) and (not move.newSquare == (0,0)))
        out.castling[2] = (out.castling[2] and (not move.oldSquare == (7,7)) and (not move.newSquare == (7,7)))
        out.castling[3] = (out.castling[3] and (not move.oldSquare == (7,0)) and (not move.newSquare == (7,0)))

        out.boardState = self.boardState.copy()
        if not (move.piece is None) and move.piece.lower() == "p" and abs(move.oldSquare[0] - move.newSquare[0]) == 2:
            out.enPassant = move.newSquare[1]
        else:
            out.enPassant = None

        out.positions = []
        out.positions.append(self.positions[0].copy())
        out.positions.append(self.positions[1].copy())

        if not (move.piece is None) and move.piece.lower() != "k":
            out.positions[out.whitesTurn].remove(move.oldSquare)
            out.positions[out.whitesTurn].append(move.newSquare)

            if move.isDirectCapture:
                out.positions[self.whitesTurn].remove(move.newSquare)
            elif move.enPassant:
                out.positions[self.whitesTurn].remove((move.oldSquare[0], move.newSquare[1]))
        else:
            if move.castleType is None:
                out.kings[out.whitesTurn] = move.newSquare

                if move.isDirectCapture:
                    out.positions[self.whitesTurn].remove(move.newSquare)
            else:
                if move.castleType == "k":
                    out.kings[out.whitesTurn] = (7, 6)

                    out.positions[out.whitesTurn].remove((7, 7))
                    out.positions[out.whitesTurn].append((7, 5))
                elif move.castleType == "q":
                    out.kings[out.whitesTurn] = (7, 2)

                    out.positions[out.whitesTurn].remove((7, 0))
                    out.positions[out.whitesTurn].append((7, 3))
                elif move.castleType == "K":
                    out.kings[out.whitesTurn] = (0, 6)

                    out.positions[out.whitesTurn].remove((0, 7))
                    out.positions[out.whitesTurn].append((0, 5))
                elif move.castleType == "Q":
                    out.kings[out.whitesTurn] = (0, 2)

                    out.positions[out.whitesTurn].remove((0, 0))
                    out.positions[out.whitesTurn].append((0, 3))
        if(move.enPassant):
            out.boardState[move.oldSquare[0]] = out.boardState[move.oldSquare[0]][:min(move.oldSquare[1], move.newSquare[1])] + "--" + out.boardState[move.oldSquare[0]][max(move.oldSquare[1], move.newSquare[1]) + 1: ]
            out.boardState[move.newSquare[0]] = out.boardState[move.newSquare[0]][: move.newSquare[1]] + move.piece + out.boardState[move.newSquare[0]][move.newSquare[1] + 1: ]
        elif not(move.castleType is None):
            if move.castleType == "K":
                out.boardState[0] = out.boardState[0][:4] + "-RK-"
                out.castling[0] = False
                out.castling[1] = False

            elif move.castleType == "Q":
                out.boardState[0] = "--KR-" + out.boardState[0][5:]
                out.castling[0] = False
                out.castling[1] = False
            elif move.castleType == "k":
                out.boardState[7] = out.boardState[7][:4] + "-rk-"
                out.castling[2] = False
                out.castling[3] = False
            elif move.castleType == "q":
                out.boardState[7] = "--kr-" + out.boardState[7][5:]
                out.castling[2] = False
                out.castling[3] = False
        else:
            out.boardState[move.newSquare[0]] = out.boardState[move.newSquare[0]][:move.newSquare[1]] + move.piece + out.boardState[move.newSquare[0]][move.newSquare[1] + 1:]
            out.boardState[move.oldSquare[0]] = out.boardState[move.oldSquare[0]][:move.oldSquare[1]] + '-' + out.boardState[move.oldSquare[0]][move.oldSquare[1] + 1:]

        if (move.isDirectCapture or move.piece.lower() == "p" or out.castling != self.castling):
            out.halfMoves = 0
            out.threeMoveDict = {}
        else:
            out.halfMoves += 1
            out.threeMoveDict = self.threeMoveDict.copy()
            if(self.threeMoveString in out.threeMoveDict):
                out.threeMoveDict[self.threeMoveString] += 1
            else:
                out.threeMoveDict[self.threeMoveString] = 1
        castleString = ""
        if out.castling[0]:
            castleString += "K"
        if out.castling[1]:
            castleString += "Q"
        if out.castling[2]:
            castleString += "k"
        if out.castling[3]:
            castleString += "q"
        out.threeMoveString =''.join(out.boardState) + castleString + ("w" if out.whitesTurn else "b") + ( "8" if out.enPassant is None else str(out.self.enPassant))
        return out

    def checkmate(self):
        return (len(self.possibleMoves) == 0) and self.kingInCheck() 
    def enoughMaterial(self):
        if(len(self.positions[0]) + len(self.positions[1]) >= 2):
            return True  
        if(len(self.positions[0]) + len(self.positions[1]) == 0):
            return False
          
        if(len(self.positions[0]) == 0):
            position = self.positions[1][0]
            piece = self.boardState[position[0]][position[1]].lower()
            return not(piece == "n" or piece == "b")
        position = self.positions[0][0]
        piece = self.boardState[position[0]][position[1]].lower()
        return not(piece == "n" or piece == "b")
    def isDraw(self):
        if (self.threeMoveString in self.threeMoveDict):
            if(self.threeMoveDict[self.threeMoveString] == 2):
                return True
        return ((len(self.possibleMoves) == 0) and not self.kingInCheck()) or self.halfMoves >= 100 or not self.enoughMaterial()

class Evaluation:
    mateWhite: bool | None
    mateIn: int | None
    eval: int | None
    result: int | None

    def __init__(self, eval : int | None = None, mateWhite: bool | None = None, mateIn: int | None = None, result: int | None = None):

        if ((mateWhite is None) != (mateIn is None)):
            raise ValueError()
        if not (((eval is None) != ((mateWhite is None) != (result is None))) and not((eval is None) and ((mateWhite is None) and (result is None)))): # Only one
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
class Bot:
    def eval(self, position: ChessBoard, depth : int):
        if depth < 0:
            raise ValueError("Depth must be non-negative")
        if position.checkmate():
            return Evaluation(result = 1 if(not position.whitesTurn) else -1)
        if position.isDraw():
            return Evaluation(result = 0)
        if depth == 0:
            return Evaluation(eval = self.heuristic(position))
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