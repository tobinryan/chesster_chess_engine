from enum import Enum


class Pieces(Enum):
    """
    Enumeration representing the types of chess pieces.

    Each piece has a corresponding integer value.
    """
    PAWN = 1
    KNIGHT = 2
    BISHOP = 3
    ROOK = 4
    QUEEN = 5
    KING = 6
