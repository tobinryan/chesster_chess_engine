import random

from Pieces import Pieces


class Hashing:

    def __init__(self, pieces):
        self.zobrist_table, self.black_move_bitstring = self.initialize_zobrist()
        self.is_black_turn = False
        self.hash_value = self.initialize_hash(pieces)
        self.game_states = {self.hash_value: 1}


    @staticmethod
    def initialize_zobrist():
        table = [[random.getrandbits(64) for _ in range(12)] for _ in range(64)]
        black_to_move_bitstring = random.getrandbits(64)
        return table, black_to_move_bitstring

    def initialize_hash(self, bitboards):
        hash_value = 0
        for i in range(64):
            for piece in range(12):
                if bitboards[piece].is_occupied(i):
                    hash_value ^= self.zobrist_table[i][self.piece_to_index(bitboards[piece].get_piece_type())]

        if self.is_black_turn:
            hash_value ^= self.black_move_bitstring

        self.is_black_turn = not self.is_black_turn

        return hash_value

    def update_hash_after_move(self, move, captured):
        source_square, dest_square, piece_type = move
        moved_piece_idx = self.piece_to_index(piece_type)
        captured_piece_type, captured_square = captured
        captured_piece_idx = self.piece_to_index(captured_piece_type)

        hash_value = self.hash_value

        hash_value ^= self.zobrist_table[source_square][moved_piece_idx]

        hash_value ^= self.zobrist_table[dest_square][moved_piece_idx]

        if captured_piece_idx != -1:
            hash_value ^= self.zobrist_table[captured_square][captured_piece_idx]

        # if self.is_black_turn:
        #     hash_value ^= self.black_move_bitstring

        self.is_black_turn = not self.is_black_turn

        self.hash_value = hash_value

        if self.hash_value in self.game_states:
            self.game_states[self.hash_value] += 1
        else:
            self.game_states[self.hash_value] = 1

    def three_move_repetition(self):
        return any(value >= 3 for value in self.game_states.values())

    @staticmethod
    def piece_to_index(piece):
        match piece:
            case Pieces.PAWN:
                return 1
            case Pieces.ROOK:
                return 2
            case Pieces.KNIGHT:
                return 3
            case Pieces.BISHOP:
                return 4
            case Pieces.QUEEN:
                return 5
            case Pieces.KING:
                return 6
        return -1
