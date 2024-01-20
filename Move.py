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

    def move_sort_key(self):
        if self.is_castle:
            return 1
        if self.is_promotion:
            return 2
        if self.is_castle:
            return 3
        return 4

    def flip(self):
        # Calculate the flipped move
        self.start_square = 63 - self.start_square
        self.end_square = 63 - self.end_square
