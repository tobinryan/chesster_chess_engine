import sys
from typing import List

import pygame

from BitBoard import BitBoard
from Hashing import Hashing
from Move import Move
from Pieces import Pieces


class Board:
    Square = int
    SQUARES = [
        A1, B1, C1, D1, E1, F1, G1, H1,
        A2, B2, C2, D2, E2, F2, G2, H2,
        A3, B3, C3, D3, E3, F3, G3, H3,
        A4, B4, C4, D4, E4, F4, G4, H4,
        A5, B5, C5, D5, E5, F5, G5, H5,
        A6, B6, C6, D6, E6, F6, G6, H6,
        A7, B7, C7, D7, E7, F7, G7, H7,
        A8, B8, C8, D8, E8, F8, G8, H8,
    ] = range(64)
    UNICODE_PIECE_SYMBOLS = {
        "r": "♖", "R": "♜",
        "n": "♘", "N": "♞",
        "b": "♗", "B": "♝",
        "q": "♕", "Q": "♛",
        "k": "♔", "K": "♚",
        "p": "♙", "P": "♟",
    }
    RANK_MASKS = [0xFF << (8 * i) for i in range(8)]
    FILE_MASKS = [0x0101010101010101 << i for i in range(8)]
    DIAG_MASKS = [0x1, 0x102, 0x10204, 0x1020408, 0x102040810, 0x10204081020, 0x1020408102040,
                  0x102040810204080, 0x204081020408000, 0x408102040800000, 0x810204080000000,
                  0x1020408000000000, 0x2040800000000000, 0x4080000000000000, 0x8000000000000000]
    ANTIDIAG_MASKS = [0x80, 0x8040, 0x804020, 0x80402010, 0x8040201008, 0x804020100804, 0x80402010080402,
                      0x8040201008040201, 0x4020100804020100, 0x2010080402010000, 0x1008040201000000,
                      0x804020100000000, 0x402010000000000, 0x201000000000000, 0x100000000000000]
    KNIGHT_SPAN = 43234889994
    KING_SPAN = 460039
    FILE_A = 72340172838076673
    FILE_H = -9187201950435737472
    FILE_AB = 217020518514230019
    FILE_GH = -4557430888798830400
    RANK_1 = 255
    RANK_4 = 4278190080
    RANK_5 = 1095216660480
    RANK_8 = -72057594037927936
    BOARD_SPAN = 0xFFFFFFFFFFFFFFFF

    # Instantiating bitBoards for each color/type of material
    wp = BitBoard(0b11111111 << 8, pygame.image.load('images/wp.png'), True, Pieces.PAWN)  # White Pawn
    bp = BitBoard(0b11111111 << 48, pygame.image.load('images/bp.png'), False, Pieces.PAWN)  # Black Pawn
    wr = BitBoard(0b10000001, pygame.image.load('images/wr.png'), True, Pieces.ROOK)  # White Rook
    br = BitBoard(0b10000001 << 56, pygame.image.load('images/br.png'), False, Pieces.ROOK)  # Black Rook
    wkn = BitBoard(0b01000010, pygame.image.load('images/wkn.png'), True, Pieces.KNIGHT)  # White Knight
    bkn = BitBoard(0b01000010 << 56, pygame.image.load('images/bkn.png'), False, Pieces.KNIGHT)  # Black Knight
    wb = BitBoard(0b00100100, pygame.image.load('images/wb.png'), True, Pieces.BISHOP)  # White Bishop
    bb = BitBoard(0b00100100 << 56, pygame.image.load('images/bb.png'), False, Pieces.BISHOP)  # Black Bishop
    wq = BitBoard(0b00001000, pygame.image.load('images/wq.png'), True, Pieces.QUEEN)  # White Queen
    bq = BitBoard(0b00001000 << 56, pygame.image.load('images/bq.png'), False, Pieces.QUEEN)  # Black Queen
    wk = BitBoard(0b00010000, pygame.image.load('images/wk.png'), True, Pieces.KING)  # White King
    bk = BitBoard(0b00010000 << 56, pygame.image.load('images/bk.png'), False, Pieces.KING)  # Black King
    pieces = [wp, bp, wr, br, wkn, bkn, wb, bb, wq, bq, wk, bk]

    def __init__(self, gui):
        self.selected: (BitBoard, int) = None  # Tuple (selected_bitboard, position)
        self.is_white_turn = True
        self.last_move = None
        self.half_move_count = 0
        self.white_can_castle = (True, True)  # Tuple (short_castle, long_castle)
        self.black_can_castle = (True, True)  # Tuple (short_castle, long_castle)
        self.Hash = Hashing(self.pieces)
        self.RANK_NAMES = ["1", "2", "3", "4", "5", "6", "7", "8"]
        self.FILE_NAMES = ["a", "b", "c", "d", "e", "f", "g", "h"]
        self.SQUARE_NAMES = [f + r for r in self.RANK_NAMES for f in self.FILE_NAMES]
        self.PIECE_SYMBOLS = {Pieces.PAWN: "p", Pieces.KNIGHT: "n", Pieces.BISHOP: "b",
                              Pieces.ROOK: "r", Pieces.QUEEN: "q", Pieces.KING: "k"}
        self.gui = gui

    @staticmethod
    def get_rank(sq: Square):
        return sq // 8

    @staticmethod
    def get_file(sq: Square):
        return sq % 8

    def get_color(self, sq: Square):
        """
        Determines the color of a chessboard square based on its position.

        Parameters:
        - position: The index of the square (0-63).

        Returns:
        True if the square is dark, False if the square is light.
        """
        return (self.get_file(sq) + self.get_rank(sq)) % 2 == 0

    def square_name(self, square: Square) -> str:
        """Gets the name of the square, like ``a3``."""
        return self.SQUARE_NAMES[square]

    @staticmethod
    def get_squares(n) -> List[Square]:
        squares = []
        while n:
            square = n.bit_length() - 1
            squares.append(square)
            n ^= 1 << square  # Clear the least significant bit
        return squares

    @staticmethod
    def lsb(n):
        return (n & -n).bit_length() - 1

    @staticmethod
    def reverse(n):
        n = ((n & 0x5555555555555555) << 1) | ((n >> 1) & 0x5555555555555555)
        n = ((n & 0x3333333333333333) << 2) | ((n >> 2) & 0x3333333333333333)
        n = ((n & 0x0F0F0F0F0F0F0F0F) << 4) | ((n >> 4) & 0x0F0F0F0F0F0F0F0F)
        n = ((n & 0x00FF00FF00FF00FF) << 8) | ((n >> 8) & 0x00FF00FF00FF00FF)
        n = ((n & 0x0000FFFF0000FFFF) << 16) | ((n >> 16) & 0x0000FFFF0000FFFF)
        n = (n << 32) | (n >> 32)
        return n

    @staticmethod
    def is_valid_square(sq: Square):
        return 0 <= sq <= 63

    def get_bb(self, piece: Pieces, is_white):
        if piece == Pieces.PAWN and is_white:
            return self.wp
        elif piece == Pieces.PAWN and not is_white:
            return self.bp
        elif piece == Pieces.BISHOP and is_white:
            return self.wb
        elif piece == Pieces.BISHOP and not is_white:
            return self.bb
        elif piece == Pieces.KNIGHT and is_white:
            return self.wkn
        elif piece == Pieces.KNIGHT and not is_white:
            return self.bkn
        elif piece == Pieces.ROOK and is_white:
            return self.wr
        elif piece == Pieces.ROOK and not is_white:
            return self.br
        elif piece == Pieces.QUEEN and is_white:
            return self.wq
        elif piece == Pieces.QUEEN and not is_white:
            return self.bq
        elif piece == Pieces.KING and is_white:
            return self.wk
        elif piece == Pieces.KING and not is_white:
            return self.bk

    def get_occupied(self):
        return self.wp.get_board() | self.bp.get_board() | self.wr.get_board() | \
               self.br.get_board() | self.wkn.get_board() | self.bkn.get_board() | self.wb.get_board() | \
               self.bb.get_board() | self.wq.get_board() | self.bq.get_board() | self.wk.get_board() | \
               self.bk.get_board()

    def get_white(self):
        return self.wp.get_board() | self.wr.get_board() | self.wkn.get_board() | \
               self.wb.get_board() | self.wq.get_board() | self.wk.get_board()

    def get_black(self):
        return self.bp.get_board() | self.br.get_board() | self.bkn.get_board() | \
               self.bb.get_board() | self.bq.get_board() | self.bk.get_board()

    def move(self, piece_to_move: (BitBoard, Square), dest_square: Square) -> bool:
        """
        Moves a chess piece to the specified destination square.

        Parameters:
        - piece_to_move: Tuple (piece, start_square) representing the piece to be moved.
        - dest_square: The index of the destination square (0-63).

        Returns:
        True if the move is successful, False otherwise.

        This method performs various checks to validate the move, updates the game state,
        handles specific piece movements (e.g., en passant, pawn promotion, castling),
        and updates game-related parameters.
        """
        piece, start_square = piece_to_move
        can_castle = self.white_can_castle if piece.is_white() else self.black_can_castle

        # Get all possible moves for the piece and remove any that result in check
        moves = self.get_moves(piece, start_square, can_castle)
        king = self.wk if self.is_white_turn else self.bk
        moves = self.remove_check_moves(piece, start_square, moves, king)

        move = self.is_valid_move(start_square, dest_square, piece.get_piece_type(), moves)

        # Check if the destination square is a valid move
        if not move:
            return False

        # Handle opponent piece if present on the destination square
        opponent_piece = self.get_opponent(dest_square, piece.is_white())

        # Handle specific piece movements (e.g. en passant, castling)
        if move.en_passant:
            self.handle_en_passant(dest_square, piece.is_white())
        if move.is_capture:
            self.handle_opponent_piece(opponent_piece, dest_square)
        if move.is_castle:
            self.handle_castling(start_square, dest_square, piece.is_white())
        if move.is_promotion:
            self.gui.promote_pawn(piece, move.end_square)

        # Update game state, including handling game-ending conditions
        self.half_move_count += 1
        self.update_can_castle(move, piece.is_white())
        self.handle_game_state_endings()

        # Reset half-move count if a capture or pawn move occurs
        if opponent_piece or move.piece_type == Pieces.PAWN:
            self.half_move_count = 0

        # Update the hash value of the current game state after the move
        self.Hash.update_hash_after_move((start_square, dest_square, piece.get_piece_type()),
                                         (opponent_piece.get_piece_type() if opponent_piece else None, dest_square))

        if not move.is_castle:
            piece.clear_square(move.start_square)
        if not move.is_castle and not move.is_promotion:
            piece.occupy_square(move.end_square)

        # Store information about the last move
        self.last_move = move

        return True

    @staticmethod
    def is_valid_move(start_sq: Square, dest_sq: Square, piece_type: Pieces, moves: List[Move]):
        """
        Checks if a given position is a valid move.

        Parameters:
        - position: The index of the position (0-63) to check.
        - moves: A bitboard representing the available moves.

        Returns:
        True if the position is a valid move, False otherwise.
        """
        target_move = Move(start_sq, dest_sq, piece_type)
        for move in moves:
            if move == target_move:
                return move
        return None

    @staticmethod
    def handle_opponent_piece(piece, sq: Square):
        """
        Handles the removal of an opponent's piece from the board.

        Parameters:
        - piece: The opponent's piece to be removed.
        - position: The index of the square where the opponent's piece is located.

        This method clears the square on the board occupied by the opponent's piece and returns true
        if a piece was captured and false otherwise.
        """
        if piece:
            piece.clear_square(sq)

    def handle_en_passant(self, dest_square, is_white):
        """
        Handles en passant captures.

        Parameters:
        - start_square: The index of the current position of the pawn.
        - is_white: True if the pawn is white, False if black.
        - dest_square: The index of the destination square of the pawn.

        This method checks for en passant captures and removes the captured opponent's pawn and returns True if
        an en passant capture was made and False otherwise.
        """
        direction = -1 if is_white else 1

        # Find and clear the square of the captured opponent's pawn
        opponent_position = dest_square + 8 * direction
        opponent_piece = self.get_opponent(opponent_position, is_white)
        if opponent_piece:
            opponent_piece.clear_square(opponent_position)
        else:
            raise Exception("Completed en passant move but couldn't find opponent piece.")

    def handle_castling(self, start_square: Square, dest_square: Square, is_white: bool):
        """
        Performs the castling maneuver for the given piece.

        Parameters:
        - piece: The piece performing castling (either king or rook).
        - start_square: The current position of the piece.
        - dest_square: The destination position after castling.

        Returns:
        True if castling is successfully performed.

        This method updates the board and castling flags based on the castling maneuver.
        """
        king = self.wk if is_white else self.bk
        rook = self.wr if is_white else self.br
        # Determine the displacements for the king and rook based on castling direction (king side or queen side)
        rook_dx = -2 if start_square < dest_square else 3
        king_dx = 2 if start_square < dest_square else -2

        # Clear the current positions of the king or rook
        king.clear_square(start_square)

        # Move the king to the new position
        king.occupy_square(start_square + king_dx)

        # Move the rook involved in castling
        rook.clear_square(dest_square)

        rook.occupy_square(dest_square + rook_dx)

        return True

    def update_can_castle(self, move: Move, is_white: bool):
        """
        Updates castling flags based on the movement of the given piece.

        Parameters:
        - piece: The piece whose movement affects castling.
        - square: The square of the piece after the move.

        This method updates the castling flags for both white and black players
        based on the movement of the given piece, especially kings and rooks.
        """

        # Update castling flags for white player
        if self.white_can_castle:
            if is_white and move.piece_type == Pieces.KING:
                self.white_can_castle = False, False
            elif is_white and move.piece_type == Pieces.ROOK:
                if self.get_file(move.start_square) == 0:
                    self.white_can_castle = self.white_can_castle[0], False
                elif self.get_file(move.start_square) == 7:
                    self.white_can_castle = False, self.white_can_castle[1]

        # Update castling flags for black player
        if self.black_can_castle:
            if not is_white and move.piece_type == Pieces.KING:
                self.black_can_castle = False, False
            elif not is_white and move.piece_type == Pieces.ROOK:
                if self.get_file(move.start_square) == 0:
                    self.black_can_castle = self.black_can_castle[0], False
                elif self.get_file(move.start_square) == 7:
                    self.black_can_castle = False, self.black_can_castle[1]

    def get_all_moves(self, bitboard: BitBoard, can_castle) -> List[Move]:
        moves = []
        positions = self.get_squares(bitboard.get_board())
        for position in positions:
            moves.extend(self.get_moves(bitboard, position, can_castle))
        return moves

    def get_moves(self, bitboard: BitBoard, position, can_castle) -> List[Move]:
        if bitboard.get_piece_type() == Pieces.PAWN:
            return self.get_pawn_moves(position, bitboard.is_white())
        elif bitboard.get_piece_type() == Pieces.KNIGHT:
            return self.get_knight_moves(position, bitboard.is_white())
        elif bitboard.get_piece_type() == Pieces.BISHOP:
            return self.get_bishop_moves(position, bitboard.is_white())
        elif bitboard.get_piece_type() == Pieces.ROOK:
            return self.get_rook_moves(position, bitboard.is_white())
        elif bitboard.get_piece_type() == Pieces.QUEEN:
            return self.get_queen_moves(position, bitboard.is_white())
        elif bitboard.get_piece_type() == Pieces.KING:
            return self.get_king_moves(position, bitboard.is_white(), can_castle)

    def hv_moves(self, sq: Square, is_white: bool) -> int:
        if not self.is_valid_square(sq):
            return 0
        binaryPos = 1 << sq
        occ = self.get_occupied()
        teammate = self.get_white() if is_white else self.get_black()
        hPoss = (occ - 2 * binaryPos) ^ self.reverse(self.reverse(occ) - (2 * self.reverse(binaryPos)))
        vPoss = ((occ & self.FILE_MASKS[self.get_file(sq)]) - (2 * binaryPos)) ^ \
                self.reverse(self.reverse(occ & self.FILE_MASKS[self.get_file(sq)]) - (2 * self.reverse(binaryPos)))
        totalPoss = (hPoss & self.RANK_MASKS[self.get_rank(sq)]) | \
                    (vPoss & self.FILE_MASKS[self.get_file(sq)])
        totalPoss &= ~teammate
        return totalPoss

    def diag_moves(self, sq: Square, is_white: bool) -> int:
        if not self.is_valid_square(sq):
            return 0
        binaryPos = 1 << sq
        occ = self.get_occupied()
        teammate = self.get_white() if is_white else self.get_black()
        diag = self.get_rank(sq) + self.get_file(sq)
        antidiag = self.get_rank(sq) + 7 - self.get_file(sq)
        diagPoss = ((occ & self.DIAG_MASKS[diag]) - 2 * binaryPos) ^ \
                   self.reverse(self.reverse(occ & self.DIAG_MASKS[diag]) - 2 * self.reverse(binaryPos))
        antiDiagPoss = ((occ & self.ANTIDIAG_MASKS[antidiag]) - 2 * binaryPos) ^ \
                       self.reverse(self.reverse(occ & self.ANTIDIAG_MASKS[antidiag]) - 2 * self.reverse(binaryPos))
        totalPoss = diagPoss & self.DIAG_MASKS[diag] | antiDiagPoss & self.ANTIDIAG_MASKS[antidiag]
        totalPoss &= ~teammate
        return totalPoss

    def get_pawn_moves(self, sq: Square, is_white) -> List[Move]:
        moves = []
        binarySq = 1 << sq
        opp = self.get_black() if is_white else self.get_white()
        occ = self.get_occupied()

        if is_white:
            possibility = (binarySq << 7) & opp & ~self.FILE_H & ~self.RANK_8
            moves.extend(Move(sq, end_square, Pieces.PAWN, True) for end_square in self.get_squares(possibility))

            possibility = (binarySq << 9) & opp & ~self.FILE_A & ~self.RANK_8
            moves.extend(Move(sq, end_square, Pieces.PAWN, True) for end_square in self.get_squares(possibility))

            possibility = (binarySq << 8) & ~occ & ~self.RANK_8
            moves.extend(Move(sq, end_square, Pieces.PAWN) for end_square in self.get_squares(possibility))

            possibility = (binarySq << 16) & ~occ & (~occ << 8) & self.RANK_4
            moves.extend(Move(sq, end_square, Pieces.PAWN) for end_square in self.get_squares(possibility))

            possibility = (binarySq << 7) & opp & ~self.FILE_H & self.RANK_8
            moves.extend(Move(sq, end_square, Pieces.PAWN, is_capture=True, is_promotion=True)
                         for end_square in self.get_squares(possibility))

            possibility = (binarySq << 9) & opp & ~self.FILE_A & self.RANK_8
            moves.extend(Move(sq, end_square, Pieces.PAWN, is_capture=True, is_promotion=True)
                         for end_square in self.get_squares(possibility))

            possibility = (binarySq << 8) & ~occ & self.RANK_8
            moves.extend(Move(sq, end_square, Pieces.PAWN, is_promotion=True)
                         for end_square in self.get_squares(possibility))

            if self.last_move:
                e_file = self.get_file(self.last_move.end_square)
                e_rank = self.get_rank(self.last_move.end_square)
                if (
                        self.last_move.piece_type == Pieces.PAWN and
                        self.get_file(self.last_move.start_square) == e_file and
                        abs(e_rank - self.get_rank(self.last_move.start_square)) == 2
                ):

                    possibility = (binarySq >> 1) & self.bp.get_board() & self.RANK_5 \
                                  & ~self.FILE_H & self.FILE_MASKS[e_file]
                    if possibility:
                        moves.append(Move(sq, sq + 7, Pieces.PAWN, en_passant=True))

                    possibility = (binarySq << 1) & self.bp.get_board() & self.RANK_5 \
                                  & ~self.FILE_A & self.FILE_MASKS[e_file]
                    if possibility:
                        moves.append(Move(sq, sq + 9, Pieces.PAWN, en_passant=True))
        else:
            possibility = (binarySq >> 7) & opp & ~self.FILE_A & ~self.RANK_1
            moves.extend(Move(sq, end_square, Pieces.PAWN, True) for end_square in self.get_squares(possibility))

            possibility = (binarySq >> 9) & opp & ~self.FILE_H & ~self.RANK_1
            moves.extend(Move(sq, end_square, Pieces.PAWN, True) for end_square in self.get_squares(possibility))

            possibility = (binarySq >> 8) & ~occ & ~self.RANK_1
            moves.extend(Move(sq, end_square, Pieces.PAWN) for end_square in self.get_squares(possibility))

            possibility = (binarySq >> 16) & ~occ & (~occ >> 8) & self.RANK_5
            moves.extend(Move(sq, end_square, Pieces.PAWN) for end_square in self.get_squares(possibility))

            possibility = (binarySq >> 7) & opp & ~self.FILE_A & self.RANK_1
            moves.extend(Move(sq, end_square, Pieces.PAWN, is_capture=True, is_promotion=True)
                         for end_square in self.get_squares(possibility))

            possibility = (binarySq >> 9) & opp & ~self.FILE_H & self.RANK_1
            moves.extend(Move(sq, end_square, Pieces.PAWN, is_capture=True, is_promotion=True)
                         for end_square in self.get_squares(possibility))

            possibility = (binarySq >> 8) & ~occ & self.RANK_1
            moves.extend(Move(sq, end_square, Pieces.PAWN, is_promotion=True)
                         for end_square in self.get_squares(possibility))

            if self.last_move:
                e_file = self.get_file(self.last_move.end_square)
                e_rank = self.get_rank(self.last_move.end_square)
                if (
                        self.last_move.piece_type == Pieces.PAWN and
                        self.get_file(self.last_move.start_square) == e_file and
                        abs(e_rank - self.get_rank(self.last_move.start_square)) == 2
                ):

                    possibility = (binarySq << 1) & self.wp.get_board() & self.RANK_4 \
                                  & ~self.FILE_A & self.FILE_MASKS[e_file]
                    if possibility:
                        moves.append(Move(sq, sq - 7, Pieces.PAWN, en_passant=True))

                    possibility = (binarySq >> 1) & self.wp.get_board() & self.RANK_4 \
                                  & ~self.FILE_H & self.FILE_MASKS[e_file]
                    if possibility:
                        moves.append(Move(sq, sq - 9, Pieces.PAWN, en_passant=True))

        return moves

    def get_knight_moves(self, sq: Square, is_white) -> List[Move]:
        occ = self.get_occupied()
        teammate = self.get_white() if is_white else self.get_black()
        if sq > 18:
            totalPoss = self.KNIGHT_SPAN << (sq - 18)
        else:
            totalPoss = self.KNIGHT_SPAN >> (18 - sq)
        if sq % 8 < 4:
            totalPoss &= ~self.FILE_GH & ~teammate
        else:
            totalPoss &= ~self.FILE_AB & ~teammate
        totalPoss &= self.BOARD_SPAN

        end_squares = self.get_squares(totalPoss)
        end_squares = [square for square in end_squares]

        return [Move(sq, end_square, Pieces.KNIGHT, 1 << end_square & occ) for end_square in end_squares]

    def get_bishop_moves(self, sq: Square, is_white: bool) -> List[Move]:
        occ = self.get_occupied()
        end_squares = self.get_squares(self.diag_moves(sq, is_white))
        return [Move(sq, end_square, Pieces.BISHOP, (1 << end_square) & occ)
                for end_square in end_squares]

    def get_rook_moves(self, sq: Square, is_white) -> List[Move]:
        end_squares = self.get_squares(self.hv_moves(sq, is_white))
        occ = self.get_occupied()
        return [Move(sq, end_square, Pieces.ROOK, (1 << end_square) & occ) for end_square in end_squares]

    def get_queen_moves(self, sq: Square, is_white: bool) -> List[Move]:
        end_squares = self.get_squares(self.hv_moves(sq, is_white) | self.diag_moves(sq, is_white))
        o = self.get_occupied()
        return [Move(sq, end_square, Pieces.QUEEN, (1 << end_square) & o) for end_square in end_squares]

    def get_king_moves(self, sq: Square, is_white: bool, can_castle) -> List[Move]:
        opp = self.get_black() if is_white else self.get_white()
        teammate = self.get_white() if is_white else self.get_black()

        if sq > 9:
            possibility = self.KING_SPAN << (sq - 9)
        else:
            possibility = self.KING_SPAN >> (9 - sq)
        if sq % 8 < 4:
            possibility &= ~self.FILE_GH & ~teammate
        else:
            possibility &= ~self.FILE_AB & ~teammate

        possibility &= self.BOARD_SPAN
        end_squares = self.get_squares(possibility)
        return [Move(sq, end_square, Pieces.KING, 1 << end_square & opp) for end_square in end_squares] + \
               self.get_castling_moves(sq, is_white, can_castle)

    def get_castling_moves(self, sq: Square, is_white, can_castle) -> List[Move]:
        moves = []
        occ = self.get_occupied()
        unsafe = self.get_unsafe(is_white)
        r = self.wr.get_board() if is_white else self.br.get_board()
        binarySq = 1 << sq
        short_castle, long_castle = can_castle
        if short_castle:
            if (unsafe & binarySq == 0) & (unsafe & (binarySq << 1) == 0) & \
                    (unsafe & (binarySq << 2) == 0) & (unsafe & (binarySq << 3) == 0):
                if (occ & (binarySq << 1) == 0) & (occ & (binarySq << 2) == 0) & (r & (binarySq << 3) != 0):
                    moves.append(Move(sq, sq + 3, Pieces.KING, is_castle=True))
        if long_castle:
            if (unsafe & binarySq == 0) & (unsafe & (binarySq >> 1) == 0) & (unsafe & (binarySq >> 2) == 0) & \
                    (unsafe & (binarySq >> 3) == 0) & (unsafe & (binarySq >> 4) == 0):
                if (occ & (binarySq >> 1) == 0) & (occ & (binarySq >> 2) == 0) & \
                        (occ & (binarySq >> 3) == 0) & (r & (binarySq >> 4) != 0):
                    moves.append(Move(sq, sq - 4, Pieces.KING, is_castle=True))
        return moves

    def get_unsafe(self, is_white: bool):
        p, r, kn, b, q, k = (self.pieces[(2 * i + is_white)].get_board() for i in range(6))

        if is_white:
            unsafe = (p >> 7) & ~self.FILE_A
            unsafe |= (p >> 9) & ~self.FILE_H

            i = kn & ~(kn - 1)
            while i != 0:
                sq = self.lsb(i)
                if sq > 18:
                    poss = self.KNIGHT_SPAN << (sq - 18)
                else:
                    poss = self.KNIGHT_SPAN >> (18 - sq)
                if sq % 8 < 4:
                    poss &= ~self.FILE_GH
                else:
                    poss &= ~self.FILE_AB
                poss &= self.BOARD_SPAN

                unsafe |= poss
                kn &= ~i
                i = kn & ~(kn - 1)

            qb = q | b
            i = qb & ~(qb - 1)
            while i != 0:
                sq = self.lsb(i)
                poss = self.diag_moves(sq, not is_white)
                unsafe |= poss
                qb &= ~i
                i = qb & ~(qb - 1)

            qr = q | r
            i = qr & ~(qr - 1)
            while i != 0:
                sq = self.lsb(i)
                poss = self.hv_moves(sq, not is_white)
                unsafe |= poss
                qr &= ~i
                i = qr & ~(qr - 1)

            sq = self.lsb(k)
            if sq > 9:
                poss = self.KING_SPAN << (sq - 9)
            else:
                poss = self.KING_SPAN >> (9 - sq)
            if sq % 8 < 4:
                poss &= ~self.FILE_GH
            else:
                poss &= ~self.FILE_AB
            poss &= self.BOARD_SPAN
            unsafe |= poss

            return unsafe
        else:
            unsafe = (p << 7) & ~self.FILE_H
            unsafe |= (p << 9) & ~self.FILE_A

            i = kn & ~(kn - 1)
            while i != 0:
                sq = self.lsb(i)
                if sq > 18:
                    poss = self.KNIGHT_SPAN << (sq - 18)
                else:
                    poss = self.KNIGHT_SPAN >> (18 - sq)
                if sq % 8 < 4:
                    poss &= ~self.FILE_GH
                else:
                    poss &= ~self.FILE_AB
                poss &= self.BOARD_SPAN

                unsafe |= poss
                kn &= ~i
                i = kn & ~(kn - 1)

            qb = q | b
            i = qb & ~(qb - 1)
            while i != 0:
                sq = self.lsb(i)
                poss = self.diag_moves(sq, not is_white)
                unsafe |= poss
                qb &= ~i
                i = qb & ~(qb - 1)

            qr = q | r
            i = qr & ~(qr - 1)
            while i != 0:
                sq = self.lsb(i)
                poss = self.hv_moves(sq, not is_white)
                unsafe |= poss
                qr &= ~i
                i = qr & ~(qr - 1)

            sq = self.lsb(k)
            if sq > 9:
                poss = self.KING_SPAN << (sq - 9)
            else:
                poss = self.KING_SPAN >> (9 - sq)
            if sq % 8 < 4:
                poss &= ~self.FILE_GH
            else:
                poss &= ~self.FILE_AB
            poss &= self.BOARD_SPAN
            unsafe |= poss

            return unsafe

    def handle_game_state_endings(self):
        """
        Handles different game state endings.

        This method checks for conditions such as checkmate, stalemate, three-move repetition,
        fifty-move rule, and insufficient material. If any of these conditions are met,
        it prints the result and exits the game.
        """
        # Check for checkmate and exit the game if found

        if self.is_checkmate(self.wk):
            print("Black won!")
            pygame.quit()
            sys.exit()
        elif self.is_checkmate(self.bk):
            print("White won!")
            pygame.quit()
            sys.exit()

        # Check for stalemate and exit the game if found
        elif self.is_stalemate(self.bk if self.is_white_turn else self.wk):
            print("Stalemate.")
            pygame.quit()
            sys.exit()

        # Check for three-move repetition and exit the game if found
        elif self.Hash.three_move_repetition():
            print("Draw - three move repetition.")
            pygame.quit()
            sys.exit()

        # Check for the fifty-move rule and exit the game if found
        elif self.half_move_count >= 100:
            print("Draw - fifty move rule.")
            pygame.quit()
            sys.exit()

        # Check for insufficient material and exit the game if found
        elif self.is_insufficient_material():
            print("Draw - insufficient material.")
            pygame.quit()
            sys.exit()

    def is_insufficient_material(self):
        """
        Checks for insufficient material conditions in the chess endgame.

        Returns:
        True if the current board state represents an insufficient material scenario, False otherwise.
        """

        # Check for non-insufficient material conditions
        if (
                self.wp.get_board() != 0
                or self.bp.get_board() != 0
                or self.wq.get_board() != 0
                or self.bq.get_board() != 0
                or self.wr.get_board() != 0
                or self.br.get_board() != 0
        ):
            return False

        # Check for King v. King endgame
        if (
                self.wb.get_board() == 0
                and self.bb.get_board() == 0
                and self.wkn.get_board() == 0
                and self.bkn.get_board() == 0
        ):
            return True

        # Check for King & Bishop v. King endgame
        if (
                self.wkn.get_board() == 0
                and self.bkn.get_board() == 0
                and (self.wb.get_board() == 0 or self.bb.get_board() == 0)
                and (
                len(self.get_squares(self.wb.get_board())) == 1
                or len(self.get_squares(self.bb.get_board())) == 1
        )
        ):
            return True

        # Check for King & Knight v. King endgame
        if (
                self.wb.get_board() == 0
                and self.bb.get_board() == 0
                and (self.wkn.get_board() == 0 or self.bkn.get_board() == 0)
                and (
                len(self.get_squares(self.wkn.get_board())) == 1
                or len(self.get_squares(self.bkn.get_board())) == 1
        )
        ):
            return True

        # Check for King & Bishop v. King & Bishop endgame (same colored-square bishops)
        if (
                self.wkn.get_board() == 0
                and self.bkn.get_board() == 0
                and len(self.get_squares(self.wb.get_board())) == 1
                and len(self.get_squares(self.bb.get_board())) == 1
                and self.get_color(self.get_squares(self.wb.get_board())[0])
                == self.get_color(self.get_squares(self.bb.get_board())[0])
        ):
            return True
        return False

    def remove_check_moves(self, piece, position, moves, king) -> List[Move]:
        filtered_moves = []
        piece.clear_square(position)
        for move in moves:
            opponent = self.get_opponent(move.end_square, piece.is_white())
            if opponent:
                opponent.clear_square(move.end_square)
            piece.occupy_square(move.end_square)
            if not self.is_check(king):
                filtered_moves.append(move)
            piece.clear_square(move.end_square)
            if opponent:
                opponent.occupy_square(move.end_square)
        piece.occupy_square(position)
        return filtered_moves

    def is_check(self, king: BitBoard) -> bool:
        unsafe = self.get_unsafe(king.is_white())
        return unsafe & king.get_board()

    def is_checkmate(self, king) -> bool:
        if not self.is_check(king):
            return False
        for piece in self.pieces:
            if piece.is_white() == king.is_white():
                positions = self.get_squares(piece.get_board())
                for position in positions:
                    moves = self.get_moves(piece, position, (False, False))
                    piece.clear_square(position)
                    for move in moves:
                        opponent = self.get_opponent(move.end_square, king.is_white())
                        if opponent:
                            opponent.clear_square(move.end_square)
                        piece.occupy_square(move.end_square)
                        if not self.is_check(king):
                            piece.clear_square(move.end_square)
                            piece.occupy_square(position)
                            if opponent:
                                opponent.occupy_square(move.end_square)
                            return False
                        if opponent:
                            opponent.occupy_square(move.end_square)
                        piece.clear_square(move.end_square)
                    piece.occupy_square(position)
        return True

    def is_stalemate(self, king):
        for piece in self.pieces:
            if piece.is_white() == king.is_white():
                positions = self.get_squares(piece.get_board())
                for position in positions:
                    moves = self.get_moves(piece, position, (False, False))
                    legal_moves = self.remove_check_moves(piece, position, moves, king)
                    if len(legal_moves) != 0:
                        return False
        return True

    def get_opponent(self, position, is_white):
        if not self.is_valid_square(position):
            return None
        for piece in self.pieces:
            if piece and piece.is_occupied(position) and not is_white == piece.is_white():
                return piece
        return None

    max_depth = 0

    def perft(self, depth):
        if depth == 0:
            return 1
        moves = []
        total_count = 0
        for piece in self.pieces:
            if piece.is_white() == self.is_white_turn:
                moves.extend(self.get_all_moves(piece, self.white_can_castle if self.is_white_turn
                else self.black_can_castle))

        for m in moves:
            self.make_move(m)
            wk = self.wk.get_board()

            bk = self.bk.get_board()
            if (((wk & self.get_unsafe(True)) == 0) & (not self.is_white_turn)) | (
                    ((bk & self.get_unsafe(False)) == 0) & self.is_white_turn):
                self.update_can_castle(m, self.is_white_turn)
                x = self.perft(depth - 1)
                if depth == self.max_depth:
                    print(self.gui.algebraic_notation(m) + ":", x)
                total_count += x
            self.undo_move(m)

        return total_count

    def make_move(self, move: Move):
        board = self.get_bb(move.piece_type, self.is_white_turn)
        board.clear_square(move.start_square)
        if move.is_capture:
            if not move.en_passant:
                move.captured = self.get_opponent(move.end_square, self.is_white_turn)
                move.captured.clear_square(move.end_square)
        self.update_can_castle(move, self.is_white_turn)
        self.last_move = move
        board.occupy_square(move.end_square)
        self.is_white_turn = not self.is_white_turn

    def undo_move(self, move: Move):
        self.is_white_turn = not self.is_white_turn
        board = self.get_bb(move.piece_type, self.is_white_turn)
        board.occupy_square(move.start_square)
        if move.captured:
            move.captured.occupy_square(move.end_square)
        if move.is_castle:
            if self.is_white_turn:
                self.white_can_castle = False, False
            else:
                self.black_can_castle = False, False
        board.clear_square(move.end_square)

    @staticmethod
    def find_differences(str1, str2):  # TODO WILL REMOVE AFTER DEBUGGING MOVEMENT
        # Split the input strings into individual pairs
        pairs1 = [pair.strip() for pair in str1.split('\n')]
        pairs2 = [pair.strip() for pair in str2.split('\n')]

        # Create dictionaries to store the counts for each pair
        counts1 = {pair.split(':')[0]: int(pair.split(':')[1]) for pair in pairs1}
        counts2 = {pair.split(':')[0]: int(pair.split(':')[1]) for pair in pairs2}

        # Find the keys that are present in one dictionary but not in the other
        keys_only_in_1 = set(counts1.keys()) - set(counts2.keys())
        keys_only_in_2 = set(counts2.keys()) - set(counts1.keys())

        # Find the keys that are present in both dictionaries but with different values
        different_values = [key for key in set(counts1.keys()) & set(counts2.keys()) if counts1[key] != counts2[key]]

        # Combine all the differences into a single list
        differences = {
            'keys_only_in_1': sorted(list(keys_only_in_1)),
            'keys_only_in_2': sorted(list(keys_only_in_2)),
            'different_values': sorted(different_values)
        }
        print("keys_only_in_1", (x for x in sorted(list(keys_only_in_1))))
        print("keys_only_in_2", (x for x in sorted(list(keys_only_in_2))))
        print(list(keys_only_in_2))

        return differences
