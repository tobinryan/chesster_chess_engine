class BitBoard:
    """
    Represents a bitboard for a type of chess piece (e.g., white pawns, black bishops).
    """

    def __init__(self, binary_num, icon, is_white, piece_type):
        """
        Initializes a BitBoard instance.

        Parameters:
        - binary_num: The binary representation of the bitboard.
        - icon: The image associated with the chess piece.
        - is_white: A boolean indicating whether the piece is white or black.
        - piece_type: The type of chess piece (e.g., pawn, bishop).
        """
        self._board = binary_num
        self._icon = icon
        self._is_white = is_white
        self._piece_type = piece_type

    def is_occupied(self, square):
        """
        Checks if a square on the bitboard is occupied by a piece.

        Parameters:
        - square: The index of the square to check.

        Returns:
        True if the square is occupied, False otherwise.
        """
        return self._board & (1 << square)

    def clear_square(self, square):
        """
        Clears a square on the bitboard, removing the piece.

        Parameters:
        - square: The index of the square to clear.
        """
        self._board &= ~(1 << square)

    def occupy_square(self, square):
        """
        Occupies a square on the bitboard, placing a piece.

        Parameters:
        - square: The index of the square to occupy.
        """
        self._board |= (1 << square)

    def get_icon(self):
        """
        Gets the icon associated with the chess piece.

        Returns:
        The icon or image.
        """
        return self._icon

    def get_board(self):
        """
        Gets the binary representation of the bitboard.

        Returns:
        The bitboard.
        """
        return self._board

    def get_piece_type(self):
        """
        Gets the type of chess piece.

        Returns:
        The piece type (e.g., pawn, bishop).
        """
        return self._piece_type

    def is_white(self):
        """
        Checks if the piece is white.

        Returns:
        True if the piece is white, False otherwise.
        """
        return self._is_white

    def clear_board(self):
        """
        Clears the binary value of the bitboard.
        """
        self._board = 0

    def __str__(self):
        """
        Returns a string representation of the bitboard in binary.

        Returns:
        A binary string representation of the bitboard.
        """
        return bin(self._board)[2:]
