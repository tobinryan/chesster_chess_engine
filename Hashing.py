import random

from Pieces import Pieces


class Hashing:
    """
    Zobrist hashing class for chess game states.

    Attributes:
    - zobrist_table: A 2D table of random bitstrings for each piece at each square.
    - black_move_bitstring: A random bitstring representing the color to move.
    - is_black_turn: A flag indicating whether it is currently black's turn.
    - hash_value: The hash value based on the current game state.
    - game_states: A dictionary storing unique hash values for encountered game states.
    """

    def __init__(self, pieces):
        """
        Initialize the Zobrist hashing for chess game states.

        Parameters:
        - pieces: The initial configuration of chess pieces.
        """
        self.zobrist_table, self.black_move_bitstring = self.initialize_zobrist()
        self.is_black_turn = False
        self.hash_value = self.initialize_hash(pieces)
        self.game_states = {self.hash_value: 1}

    @staticmethod
    def initialize_zobrist():
        """
        Initialize the Zobrist table and the bitstring for black to move.

        Returns:
        A tuple containing the Zobrist table and the bitstring for black to move.
        """
        table = [[random.getrandbits(64) for _ in range(12)] for _ in range(64)]
        black_to_move_bitstring = random.getrandbits(64)
        return table, black_to_move_bitstring

    def initialize_hash(self, bitboards):
        """
        Initialize the hash value based on the current board configuration.

        Parameters:
        - bitboards: A list of BitBoard instances representing the current piece positions.

        Returns:
        The computed hash value based on the Zobrist hashing scheme.
        """
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
        """
        Update the hash value after a chess piece move.

        Parameters:
        - move: A tuple (source_square, dest_square, piece_type) representing the moved piece.
        - captured: A tuple (captured_piece_type, captured_square) representing a captured piece.

        Modifies the hash value based on the Zobrist hashing scheme after the move and captures.
        """

        source_square, dest_square, piece_type = move
        moved_piece_idx = self.piece_to_index(piece_type)
        captured_piece_type, captured_square = captured
        captured_piece_idx = self.piece_to_index(captured_piece_type)

        hash_value = self.hash_value

        # XOR out the piece from the source square and XOR in the piece to the destination square
        hash_value ^= self.zobrist_table[source_square][moved_piece_idx]
        hash_value ^= self.zobrist_table[dest_square][moved_piece_idx]

        # If a piece is captured, XOR out the captured piece from its square
        if captured_piece_idx != -1:
            hash_value ^= self.zobrist_table[captured_square][captured_piece_idx]

        # XOR in the bit representing the color to move
        if self.is_black_turn:
            hash_value ^= self.black_move_bitstring

        self.is_black_turn = not self.is_black_turn
        self.hash_value = hash_value

        # Update the game states dictionary
        if self.hash_value in self.game_states:
            self.game_states[self.hash_value] += 1
        else:
            self.game_states[self.hash_value] = 1

    def three_move_repetition(self):
        """
        Check if any board state has occurred three or more times during the game.

        Returns:
        True if s board state has occurred three or more times, False otherwise.
        """
        return any(value >= 3 for value in self.game_states.values())

    @staticmethod
    def piece_to_index(piece):
        """
        Map a piece type to its corresponding index for Zobrist hashing.

        Parameters:
        - piece: The Pieces enumeration representing a chess piece.

        Returns:
        An integer index for the given piece type.
        """
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
