from Pieces import Pieces


class Move:
    def __init__(self, start_square: int, end_square: int, piece_type: Pieces, is_capture: bool = False,
                 en_passant: bool = False, is_castle: bool = False, is_promotion: bool = False):
        self.start_square = start_square
        self.end_square = end_square
        self.piece_type = piece_type
        self.is_capture = is_capture
        self.en_passant = en_passant
        self.is_castle = is_castle
        self.is_promotion = is_promotion
        self.captured = None

    def __eq__(self, other):
        if isinstance(other, Move):
            return (self.start_square == other.start_square and
                    self.end_square == other.end_square)
        return False
