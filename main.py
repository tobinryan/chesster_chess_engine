import datetime
import math
import random
from typing import List

import pygame
import sys

from BitBoard import BitBoard
from Hashing import Hashing
from Move import Move
from Pieces import Pieces
from PromotionPopup import PromotionPopup


class ChessGUI:
    WIDTH, HEIGHT, SQUARE_SIZE = 800, 800, 100
    FPS = 60
    HIGHLIGHT_COLOR = (224, 244, 64, 100)
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
        "R": "♖", "r": "♜",
        "N": "♘", "n": "♞",
        "B": "♗", "b": "♝",
        "Q": "♕", "q": "♛",
        "K": "♔", "k": "♚",
        "P": "♙", "p": "♟",
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

    board = pygame.image.load('images/board.png')

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

    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Chester the Chess Engine")
        self.clock = pygame.time.Clock()
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
        self.capture_sound = pygame.mixer.Sound("sounds/capture.ogg")
        self.castle_sound = pygame.mixer.Sound("sounds/castle.ogg")
        self.check_sound = pygame.mixer.Sound("sounds/move-check.ogg")
        self.move_sound = pygame.mixer.Sound("sounds/move-self.ogg")
        self.promote_sound = pygame.mixer.Sound("sounds/promote.ogg")

    def coordinates_to_square(self, coordinates) -> Square:
        """
        Converts pixel coordinates on the screen to the corresponding chess board position.

        Parameters:
        - coordinates: Tuple (x, y) representing the pixel coordinates.

        Returns:
        The chess board square as a single integer (0-63).
        """
        x, y = math.floor(coordinates[0] / self.SQUARE_SIZE), math.floor(coordinates[1] / self.SQUARE_SIZE)
        return (7 - y) * 8 + x

    def run(self):
        """
        Main game loop responsible for running the chess GUI.

        This function initializes the game, handles user input, and updates the display.
        """
        running = True
        self.draw_board(None)  # Initial drawing of the chess board
        while running:
            self.clock.tick(self.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_click(pygame.mouse.get_pos())

            pygame.display.flip()

        # Clean up and exit the game
        pygame.quit()
        sys.exit()

    def draw_highlighted_piece(self):
        """
        Draws a highlighted box around the selected piece on the chess board.

        The highlighted box is drawn on the screen using a semi-transparent color.
        """
        highlighted_box = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE), pygame.SRCALPHA)
        highlighted_box.fill(self.HIGHLIGHT_COLOR)
        self.screen.blit(highlighted_box, (self.SQUARE_SIZE * (self.selected[1] % 8),
                                           700 - self.SQUARE_SIZE * (self.selected[1] // 8)))

    def draw_moves(self, moves):
        """
        Draws circles on the chess board to highlight valid moves.

        Parameters:
        - moves: A binary bitboard representing the valid moves for the selected piece.

        Two types of circles are drawn:
        - Large circle for capturing moves.
        - Small circle for non-capturing moves.

        The circles are drawn using a semi-transparent color.
        """
        small_circle_box = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(small_circle_box, (0, 0, 0, 32), (self.SQUARE_SIZE // 2, self.SQUARE_SIZE // 2), 20)
        large_circle_box = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(large_circle_box, (0, 0, 0, 32), (self.SQUARE_SIZE // 2, self.SQUARE_SIZE // 2), 50, 10)

        for move in moves:
            if move.is_castle:
                # Large circle for castling moves
                self.screen.blit(large_circle_box, (self.SQUARE_SIZE * (move.end_square % 8),
                                                    700 - self.SQUARE_SIZE * (move.end_square // 8)))
            if self.wk.is_occupied(move.end_square) or self.bk.is_occupied(move.end_square):
                # Avoid highlighting the king's square
                continue
            elif move.is_capture:
                # Large circle for capturing moves
                self.screen.blit(large_circle_box, (self.SQUARE_SIZE * (move.end_square % 8),
                                                    700 - self.SQUARE_SIZE * (move.end_square // 8)))
            else:
                # Small circle for non-capturing moves
                self.screen.blit(small_circle_box, (self.SQUARE_SIZE * (move.end_square % 8),
                                                    700 - self.SQUARE_SIZE * (move.end_square // 8)))

    def draw_board(self, moves):
        """
        Draws the chess board with pieces and move highlights.

        Parameters:
        - moves: A bitboard representing the valid moves for the selected piece.

        This method draws the chess board background, highlights the selected piece
        (if any), highlights valid moves, and places pieces on the board. The pieces
        are drawn based on their positions, and move highlights are drawn if provided.
        """

        # Draw the chess board background
        self.screen.blit(self.board, (0, 0))

        # Draw a highlighted box around the selected piece (if any)
        if self.selected is not None:
            self.draw_highlighted_piece()

        # Draw circles to highlight valid moves (if provided)
        if moves is not None:
            self.draw_moves(moves)

        # Draw pieces on the board
        for i in range(64):
            piece = self.get_piece(i)
            if piece:
                self.screen.blit(piece.get_icon(), (self.SQUARE_SIZE * (i % 8), 700 - self.SQUARE_SIZE * (i // 8)))

    @staticmethod
    def get_rank(position):
        return position // 8

    @staticmethod
    def get_file(position):
        return position % 8

    def handle_mouse_click(self, coordinates):
        """
        Handles a mouse click event on the chess board.

        Parameters:
        - coordinates: Tuple (x, y) representing the pixel coordinates of the mouse click.

        This method converts the mouse click coordinates to a square, checks the validity
        of the clicked square, and calls the appropriate method to handle the turn.
        """

        clicked_square = self.coordinates_to_square(coordinates)
        clicked_piece = self.get_piece(clicked_square)

        # Check if the clicked square is a valid position
        if not self.is_valid_position(clicked_square):
            return

        # Check if it's the first click and a valid piece is selected
        if self.selected is None and clicked_piece is not None:
            if self.is_white_turn != clicked_piece.is_white():
                print("Can't move enemy piece.")
                return

        # Handle the turn based on the selected piece and clicked square (source or destination)
        self.handle_turn(clicked_piece, clicked_square)

    def handle_turn(self, clicked_piece, clicked_square: Square):
        """
        Handles a player's turn in the chess game.

        Parameters:
        - clicked_piece: The BitBoard instance representing the piece on the clicked square.
        - clicked_square: The index of the clicked square (0-63).

        This method determines the actions to be taken based on the player's turn,
        the selected piece, and the clicked square. It also updates the displayed board.
        """

        if self.selected:
            # If a piece is already selected, handle the second click
            self.handle_second_click(clicked_piece, clicked_square)
        elif clicked_piece:
            # If no piece is selected, set the selected piece and display valid moves
            self.selected = clicked_piece, clicked_square

            # Determine available moves based on the selected piece and update the displayed board
            short_castle, long_castle = self.white_can_castle if self.selected[0].is_white() else self.black_can_castle
            king = self.wk if self.is_white_turn else self.bk
            moves = self.get_moves(self.selected[0], self.selected[1], (short_castle, long_castle))
            moves = self.remove_check_moves(self.selected[0], self.selected[1], moves,
                                            king, (short_castle, long_castle))
            self.draw_board(moves)

    def handle_second_click(self, clicked_piece: BitBoard, clicked_square: Square):
        """
        Handles the click (after selecting a piece) during a player's turn.

        Parameters:
        - clicked_piece: The BitBoard instance representing the piece on the clicked square.
        - clicked_square: The index of the clicked square (0-63).

        This method checks if the move is valid and updates the game state accordingly.
        It handles the completion of the player's turn, toggles the turn, and updates the display.
        """
        if self.move_piece(self.selected, clicked_square):
            # If the move is successful, toggle the turn and reset the selected piece
            self.is_white_turn = not self.is_white_turn
            print(self.move_notation())
            self.selected = None
            moves = None
        elif self.get_piece(clicked_square) and not \
                self.get_opponent(clicked_square, self.selected[0].is_white()) \
                and clicked_square != self.selected[1]:
            # If the clicked square is a different friendly piece, update the selected piece and display valid moves
            self.selected = clicked_piece, clicked_square
            can_castle = self.white_can_castle if clicked_piece.is_white() else self.black_can_castle
            king = self.wk if self.is_white_turn else self.bk
            moves = self.get_moves(clicked_piece, clicked_square, can_castle)
            moves = self.remove_check_moves(clicked_piece, clicked_square, moves, king, can_castle)
        else:
            # If the same piece is clicked a second time, unhighlight the piece and moves
            self.selected = None
            moves = None

        # Update the displayed board based on the updated game state
        self.draw_board(moves)

    def move_piece(self, piece_to_move: (BitBoard, Square), dest_square: Square) -> bool:
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
        moves = self.remove_check_moves(piece, start_square, moves, king, can_castle)

        # Check if the destination square is a valid move
        if not self.is_valid_move(dest_square, moves):
            print("Not a valid move.")
            return False

        # Handle opponent piece if present on the destination square
        opponent_piece = self.get_opponent(dest_square, piece.is_white())
        is_capture = self.handle_opponent_piece(opponent_piece, dest_square)
        en_passant = False

        # Handle specific piece movements (e.g. en passant, castling)
        if piece.get_piece_type() == Pieces.PAWN:
            en_passant = self.handle_en_passant(start_square, piece.is_white(), dest_square)
        elif piece.get_piece_type() in {Pieces.KING, Pieces.ROOK}:
            if self.handle_castling_moves(piece, start_square, dest_square):
                self.half_move_count += 1
                pygame.mixer.Sound.play(self.castle_sound)
                return True

        # Update game state, including handling game-ending conditions
        self.half_move_count += 1
        self.update_can_castle(piece, start_square)
        move = Move(start_square, dest_square, piece.get_piece_type(), is_capture, en_passant)
        self.finalize_move(piece, move)
        self.handle_game_state_endings()

        # Reset half-move count if a capture or pawn move occurs
        if opponent_piece or piece.get_piece_type() == Pieces.PAWN:
            self.half_move_count = 0

        # Update the hash value of the current game state after the move
        self.Hash.update_hash_after_move((start_square, dest_square, piece.get_piece_type()),
                                         (opponent_piece.get_piece_type() if opponent_piece else None, dest_square))

        pygame.mixer.Sound.play(self.move_sound)
        return True

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

    @staticmethod
    def is_valid_move(position, moves: List[Move]):
        """
        Checks if a given position is a valid move.

        Parameters:
        - position: The index of the position (0-63) to check.
        - moves: A bitboard representing the available moves.

        Returns:
        True if the position is a valid move, False otherwise.
        """
        return any(move.end_square == position for move in moves)

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
            print("King v. King")
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
            print("King & Bishop v. King")
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
            print("King & Knight v. King")
            return True

        # Check for King & Bishop v. King & Bishop endgame (same colored-square bishops)
        if (
                self.wkn.get_board() == 0
                and self.bkn.get_board() == 0
                and len(self.get_squares(self.wb.get_board())) == 1
                and len(self.get_squares(self.bb.get_board())) == 1
                and self.get_square_color(self.get_squares(self.wb.get_board())[0])
                == self.get_square_color(self.get_squares(self.bb.get_board())[0])
        ):
            print("king and bishop vs king and bishop")
            return True
        return False

    def get_square_color(self, square: Square):
        """
        Determines the color of a chessboard square based on its position.

        Parameters:
        - position: The index of the square (0-63).

        Returns:
        True if the square is dark, False if the square is light.
        """
        return (self.get_file(square) + self.get_rank(square)) % 2 == 0

    def handle_opponent_piece(self, piece, square: Square) -> bool:
        """
        Handles the removal of an opponent's piece from the board.

        Parameters:
        - piece: The opponent's piece to be removed.
        - position: The index of the square where the opponent's piece is located.

        This method clears the square on the board occupied by the opponent's piece and returns true
        if a piece was captured and false otherwise.
        """
        if piece:
            print("Took opponent piece {}.".format(piece.get_piece_type()))
            piece.clear_square(square)
            pygame.mixer.Sound.play(self.capture_sound)
            return True
        return False

    def handle_en_passant(self, start_square, is_white, dest_square) -> bool:
        """
        Handles en passant captures.

        Parameters:
        - start_square: The index of the current position of the pawn.
        - is_white: True if the pawn is white, False if black.
        - dest_square: The index of the destination square of the pawn.

        This method checks for en passant captures and removes the captured opponent's pawn and returns True if
        an en passant capture was made and False otherwise.
        """

        # Get en passant moves for the current pawn
        en_passant_moves = self.get_en_passant(start_square, is_white)

        # Check if the destination square is an en passant capture
        if self.is_valid_move(dest_square, en_passant_moves):
            direction = -1 if is_white else 1

            # Find and clear the square of the captured opponent's pawn
            opponent_position = dest_square + 8 * direction
            opponent_piece = self.get_opponent(opponent_position, is_white)
            if opponent_piece:
                opponent_piece.clear_square(opponent_position)
            else:
                raise Exception("Completed en passant move but couldn't find opponent piece.")
            return True
        return False

    def handle_castling_moves(self, piece, start_square, dest_square):
        """
        Handles castling moves for the given piece.

        Parameters:
        - piece: The piece attempting to castle.
        - start_square: The current position of the piece.
        - dest_square: The destination square after castling.

        Returns:
        True if the move involves castling, False otherwise.

        This method checks if the move involves castling based on the piece, current position,
        and next position. If castling is valid, it performs the castling maneuver and returns True.
        """

        can_castle = self.white_can_castle if piece.is_white() else self.black_can_castle
        # Get available castling moves for the piece
        castling_moves = self.get_castling_moves(
            start_square, can_castle, piece.is_white(), piece.get_piece_type()
        )

        # Check if the next position is a valid castling move
        if self.is_valid_move(dest_square, castling_moves):
            # Perform castling maneuver
            self.perform_castling(piece, start_square, dest_square)
            return True

        return False

    def perform_castling(self, piece, start_square, dest_square):
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

        # Determine the displacements for the king and rook based on castling direction (king side or queen side)
        if piece.get_piece_type() == Pieces.ROOK:
            rook_dx = 3 if start_square < dest_square else -2
            king_dx = -2 if start_square < dest_square else 2
        else:
            rook_dx = -2 if start_square < dest_square else 3
            king_dx = 2 if start_square < dest_square else -2

        # Clear the current positions of the king or rook
        piece.clear_square(start_square)

        if piece.get_piece_type() == Pieces.KING:
            # Move the king to the new position
            piece.occupy_square(start_square + king_dx)
        else:
            # Move the rook to the new position
            piece.occupy_square(start_square + rook_dx)

        # Find and move the other piece involved in castling (rook or king)
        other_piece = self.get_piece(dest_square)
        other_piece.clear_square(dest_square)

        if other_piece.get_piece_type() == Pieces.KING:
            other_piece.occupy_square(dest_square + king_dx)
        else:
            other_piece.occupy_square(dest_square + rook_dx)

        # Update castling flags
        if piece.is_white():
            self.white_can_castle = False, False
        else:
            self.black_can_castle = False, False

        return True

    def finalize_move(self, piece, move: Move):
        """
        Finalizes a chess move by updating castling flags, moving pieces,
        checking for pawn promotion, and storing information about the move.

        Parameters:
        - piece: The piece making the move.
        - start_square: The current position of the piece.
        - dest_square: The destination position after the move.
        - opponent_piece: The opponent's piece captured during the move.

        This method performs necessary actions to complete a chess move,
        including updating castling flags, moving pieces on the board,
        checking for pawn promotion, and storing information about the move.
        """

        # Update castling flags
        self.update_can_castle(piece, move.start_square)

        # Clear the current square and occupy the destination square with the piece
        piece.clear_square(move.start_square)
        piece.occupy_square(move.end_square)
        # Check for pawn promotion
        if self.pawn_reached_end(piece, move.end_square):
            pygame.mixer.Sound.play(self.promote_sound)
            self.promote_pawn(piece, move.end_square)

        # Store information about the last move
        self.last_move = move

    def update_can_castle(self, piece, square):
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
            if piece.is_white() and piece.get_piece_type() == Pieces.KING:
                self.white_can_castle = False, False
            elif piece.is_white() and piece.get_piece_type() == Pieces.ROOK:
                if self.get_file(square) == 0:
                    self.white_can_castle = self.white_can_castle[0], False
                elif self.get_file(square) == 7:
                    self.white_can_castle = False, self.white_can_castle[1]

        # Update castling flags for black player
        if self.black_can_castle:
            if not piece.is_white() and piece.get_piece_type() == Pieces.KING:
                self.black_can_castle = False, False
            elif not piece.is_white() and piece.get_piece_type() == Pieces.ROOK:
                if self.get_file(square) == 0:
                    self.black_can_castle = self.black_can_castle[0], False
                elif self.get_file(square) == 7:
                    self.black_can_castle = False, self.black_can_castle[1]

    def promote_pawn(self, bitboard: BitBoard, square: Square):
        """
        Promotes a pawn to a higher-value piece.

        Parameters:
        - bitboard: The BitBoard representing the pawn to be promoted.
        - square: The square of the pawn on the board.

        This method clears the square occupied by the pawn and displays a promotion popup,
        allowing the player to choose the promoted piece. It handles the player's choice
        and updates the board accordingly.
        """

        # Clear the square occupied by the pawn
        bitboard.clear_square(square)

        # Display the promotion popup
        promotion_popup = PromotionPopup(self.screen, [piece for piece in self.pieces if
                                                       piece.is_white() == bitboard.is_white()])
        promotion_popup.draw()

        # Wait for the player to make a choice
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Handle the player's click and the chosen promotion piece
                    click_position = pygame.mouse.get_pos()
                    promotion_choice = promotion_popup.handle_click(click_position)
                    if promotion_choice:
                        self.handle_promotion_choice(square, bitboard.is_white(), promotion_choice)
                        return

            promotion_popup.draw()
            pygame.display.flip()

    def handle_promotion_choice(self, square, is_white, promotion_choice):
        """
        Handles the player's choice of a promotion piece and updates the board.

        Parameters:
        - square: The square on the board where the promotion occurred.
        - is_white: A boolean indicating whether the promoting pawn is white.
        - promotion_choice: The type of piece chosen for promotion.

        This method locates the corresponding piece in the pieces list based on the
        promotion choice, color, and occupies the promotion square with the chosen piece.
        """
        for piece in self.pieces:
            # Find the corresponding piece for the promotion choice and color
            if piece == promotion_choice and piece.is_white() == is_white:
                # Occupy the promotion square with the chosen piece
                piece.occupy_square(square)

    def square_name(self, square: Square) -> str:
        """Gets the name of the square, like ``a3``."""
        return self.SQUARE_NAMES[square]

    def move_notation(self):
        move = ""
        piece = self.PIECE_SYMBOLS[self.last_move.piece_type]
        piece = self.UNICODE_PIECE_SYMBOLS[piece.upper() if self.is_white_turn else piece]
        move += piece
        if self.last_move.is_capture and self.last_move.piece_type == Pieces.PAWN or self.last_move.en_passant:
            move += self.FILE_NAMES[self.get_file(self.last_move.start_square)] + "x"
        elif self.last_move.is_capture:
            move += "x"
        move += self.square_name(self.last_move.end_square)
        return move

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
            return self.get_rook_moves(position, bitboard.is_white(), can_castle)
        elif bitboard.get_piece_type() == Pieces.QUEEN:
            return self.get_queen_moves(position, bitboard.is_white())
        elif bitboard.get_piece_type() == Pieces.KING:
            return self.get_king_moves(position, bitboard.is_white(), can_castle)

    def get_pawn_moves(self, sq: Square, is_white) -> List[Move]:
        moves = []
        binarySq = 1 << sq
        opp = self.get_black() if is_white else self.get_white()
        occ = self.get_occupied()

        if is_white:
            possibility = (binarySq << 7) & opp & ~self.FILE_A & ~self.RANK_8
            moves.extend(Move(sq, end_square, Pieces.PAWN, True) for end_square in self.get_squares(possibility))

            possibility = (binarySq << 9) & opp & ~self.FILE_H & ~self.RANK_8
            moves.extend(Move(sq, end_square, Pieces.PAWN, True) for end_square in self.get_squares(possibility))

            possibility = (binarySq << 8) & ~occ & ~self.RANK_8
            moves.extend(Move(sq, end_square, Pieces.PAWN) for end_square in self.get_squares(possibility))

            possibility = (binarySq << 16) & ~occ & (~occ << 8) & self.RANK_4
            moves.extend(Move(sq, end_square, Pieces.PAWN) for end_square in self.get_squares(possibility))

            possibility = (binarySq << 7) & opp & ~self.FILE_A & self.RANK_8
            moves.extend(Move(sq, end_square, Pieces.PAWN, is_capture=True, is_promotion=True)
                         for end_square in self.get_squares(possibility))

            possibility = (binarySq << 9) & opp & ~self.FILE_H & self.RANK_8
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
                        moves.append(Move(sq, sq + 7, Pieces.PAWN, True, True))

                    possibility = (binarySq << 1) & self.bp.get_board() & self.RANK_5 \
                                  & ~self.FILE_A & self.FILE_MASKS[e_file]
                    if possibility:
                        moves.append(Move(sq, sq + 9, Pieces.PAWN, True, True))
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
                        moves.append(Move(sq, sq - 7, Pieces.PAWN, True, True))

                    possibility = (binarySq >> 1) & self.wp.get_board() & self.RANK_4 \
                                  & ~self.FILE_H & self.FILE_MASKS[e_file]
                    if possibility:
                        moves.append(Move(sq, sq - 9, Pieces.PAWN, True, True))

        return moves

    def get_en_passant(self, position, is_white) -> List[Move]:
        opponent_rank = 6 if is_white else 1
        my_rank = 4 if is_white else 3
        moves = []
        if self.get_file(position) > 0 and \
                self.get_rank(position) == my_rank \
                and self.is_occupied_opponent(position - 1, is_white):
            if self.get_opponent(position - 1, is_white).get_piece_type() == Pieces.PAWN:
                if self.last_move.end_square == position - 1 and self.get_rank(
                        self.last_move.start_square) == opponent_rank:
                    if is_white:
                        moves.append(Move(position, position + 7, Pieces.PAWN, True, True))
                    else:
                        moves.append(Move(position, position - 9, Pieces.PAWN, True, True))
        if self.get_file(position) < 7 and \
                self.get_rank(position) == my_rank and \
                self.is_occupied_opponent(position + 1, is_white):
            if self.last_move.end_square == position + 1 and self.get_rank(
                    self.last_move.start_square) == opponent_rank:
                if self.get_opponent(position + 1, is_white).get_piece_type() == Pieces.PAWN:
                    if is_white:
                        moves.append(Move(position, position + 9, Pieces.PAWN, True, True))
                    else:
                        moves.append(Move(position, position - 7, Pieces.PAWN, True, True))
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

        end_squares = self.get_squares(totalPoss)
        end_squares = [square for square in end_squares if 0 <= square <= 63]

        return [Move(sq, end_square, Pieces.ROOK, 1 << end_square & occ) for end_square in end_squares]

    def get_bishop_moves(self, sq: Square, is_white: bool) -> List[Move]:
        occ = self.get_occupied()
        end_squares = self.diag_moves(sq, is_white)
        return [Move(sq, end_square, Pieces.BISHOP, 1 << end_square & occ)
                for end_square in end_squares]

    def hv_moves(self, sq: Square, is_white: bool) -> List[Square]:
        if not self.is_valid_position(sq):
            return []
        binaryPos = 1 << sq
        occ = self.get_occupied()
        teammate = self.get_white() if is_white else self.get_black()
        hPoss = (occ - 2 * binaryPos) ^ self.reverse(self.reverse(occ) - (2 * self.reverse(binaryPos)))
        vPoss = ((occ & self.FILE_MASKS[self.get_file(sq)]) - (2 * binaryPos)) ^ \
                self.reverse(self.reverse(occ & self.FILE_MASKS[self.get_file(sq)]) - (2 * self.reverse(binaryPos)))
        totalPoss = (hPoss & self.RANK_MASKS[self.get_rank(sq)]) | \
                    (vPoss & self.FILE_MASKS[self.get_file(sq)])
        totalPoss &= ~teammate
        end_squares = self.get_squares(totalPoss)
        return end_squares

    def diag_moves(self, sq: Square, is_white: bool) -> List[Square]:
        if not self.is_valid_position(sq):
            return []
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
        end_squares = self.get_squares(totalPoss)
        return end_squares

    def get_rook_moves(self, sq: Square, is_white, can_castle) -> List[Move]:  # TODO ADD CASTLING
        end_squares = self.hv_moves(sq, is_white)
        occ = self.get_occupied()
        return [Move(sq, end_square, Pieces.ROOK, 1 << end_square & occ) for end_square in end_squares]

    def get_castling_moves(self, position, can_castle, is_white, piece_type) -> List[Move]:
        moves = []
        short_castle, long_castle = can_castle
        if not (short_castle or long_castle):
            return moves

        if piece_type == Pieces.KING:
            moves.extend(self.get_king_castling_moves(position, is_white, short_castle, long_castle))
        elif piece_type == Pieces.ROOK:
            moves.extend(self.get_rook_castling_moves(position, is_white, short_castle, long_castle))

        return moves

    def get_king_castling_moves(self, sq: Square, is_white, short_castle, long_castle) -> List[Move]:
        moves = []
        dx = [i for i in range(1, 4)]
        if short_castle:
            if not any(self.is_occupied(sq + offset) for offset in dx[:2]):
                rook = self.get_teammate(sq + 3, is_white)
                if rook is not None and rook.get_piece_type() == Pieces.ROOK and rook.is_white() == is_white:
                    moves.append(Move(sq, sq + 3, Pieces.KING, is_castle=True))
        if long_castle:
            if not any(self.is_occupied(sq - offset) for offset in dx):
                rook = self.get_teammate(sq - 4, is_white)
                if rook is not None and rook.get_piece_type() == Pieces.ROOK and rook.is_white() == is_white:
                    moves.append(Move(sq, sq - 4, Pieces.KING, is_castle=True))
        return moves

    def get_rook_castling_moves(self, position, is_white, short_castle, long_castle) -> List[Move]:
        moves = []
        direction = 1 if self.get_file(position) == 0 else -1 if self.get_file(position) == 7 else 0
        dx = [position + direction * i for i in range(1, 4)]

        if direction == 1:
            if long_castle:
                if not any(self.is_occupied(pos) for pos in dx):
                    king = self.get_teammate(position + 4, is_white)
                    if king is not None and king.get_piece_type() == Pieces.KING and king.is_white() == is_white:
                        moves.append(Move(position, position + 4, Pieces.ROOK, is_castle=True))
        elif direction == -1:
            if short_castle:
                if not any(self.is_occupied(pos) for pos in dx[:-1]):
                    king = self.get_teammate(position - 3, is_white)
                    if king is not None and king.get_piece_type() == Pieces.KING and king.is_white() == is_white:
                        moves.append(Move(position, position - 3, Pieces.ROOK, is_castle=True))
        return moves

    def get_queen_moves(self, sq: Square, is_white: bool) -> List[Move]:
        end_squares = self.hv_moves(sq, is_white) + self.diag_moves(sq, is_white)
        o = self.get_occupied()
        return [Move(sq, end_square, Pieces.QUEEN, 1 << end_square & o) for end_square in end_squares]

    def get_king_moves(self, sq: Square, is_white: bool, can_castle) -> List[Move]:
        opp = self.get_black() if is_white else self.get_white()
        teammate = self.get_white() if is_white else self.get_black()

        if sq > 9:
            possibility = self.KING_SPAN << (sq - 9)
        else:
            possibility = self.KING_SPAN >> (9 - sq)
        if possibility % 8 < 4:
            possibility &= ~self.FILE_GH & ~teammate
        else:
            possibility &= ~self.FILE_AB & ~teammate

        end_squares = self.get_squares(possibility)
        return [Move(sq, end_square, Pieces.KING, 1 << end_square & opp) for end_square in end_squares]

        # moves = []
        # directions = [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]
        # for dx, dy in directions:
        #     new_position = position + (dy * 8) + dx
        #     is_occupied = self.is_occupied_opponent(new_position, is_white)
        #     if (dx == -1 and self.get_file(new_position) == 7) or (dx == 1 and self.get_file(new_position) == 0):
        #         continue
        #     elif self.is_valid_position(new_position) and (
        #             not self.is_occupied(new_position) or is_occupied):
        #         moves.append(Move(position, new_position, Pieces.KING, is_occupied))
        #
        # moves.extend(self.get_castling_moves(position, can_castle, is_white, Pieces.KING))
        # return moves

    @staticmethod
    def get_squares(bitboard) -> List[Square]:
        squares = []
        while bitboard:
            square = bitboard.bit_length() - 1
            squares.append(square)
            bitboard ^= 1 << square  # Clear the least significant bit
        return squares

    @staticmethod
    def is_valid_position(position):
        return 0 <= position <= 63

    @staticmethod
    def pawn_reached_end(bitboard, position):
        return bitboard.get_piece_type() == Pieces.PAWN and \
               ((bitboard.is_white() and position >= 56) or
                (not bitboard.is_white() and position <= 7))

    def remove_check_moves(self, piece, position, moves, king, can_castle) -> List[Move]:
        filtered_moves = []
        piece.clear_square(position)
        for move in moves:
            opponent = self.get_opponent(move.end_square, piece.is_white())
            if opponent:
                opponent.clear_square(move.end_square)
            piece.occupy_square(move.end_square)
            if not self.is_check(king, can_castle):
                filtered_moves.append(move)
            piece.clear_square(move.end_square)
            if opponent:
                opponent.occupy_square(move.end_square)
        piece.occupy_square(position)
        return filtered_moves

    def is_check(self, king: BitBoard, can_castle) -> bool:
        for bitboard in self.pieces:
            if bitboard.is_white() != king.is_white():
                for move in self.get_all_moves(bitboard, can_castle):
                    if move.end_square == self.lowest_set_bit(king.get_board()):
                        return True
        return False

    @staticmethod
    def lowest_set_bit(n):
        return (n & -n).bit_length() - 1

    def is_checkmate(self, king) -> bool:  # opponent is opposite of king
        if not self.is_check(king, (False, False)):
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
                        if not self.is_check(king, (False, False)):
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
                    legal_moves = self.remove_check_moves(piece, position, moves, king, (False, False))
                    if len(legal_moves) != 0:
                        return False
        return True

    def is_occupied_opponent(self, position, is_white):
        if not self.is_valid_position(position):
            return False
        if is_white:
            opponent = self.bp.get_board() | self.br.get_board() | self.bkn.get_board() | self.bb.get_board() | \
                       self.bq.get_board() | self.bk.get_board()
        else:
            opponent = self.wp.get_board() | self.wr.get_board() | self.wkn.get_board() | self.wb.get_board() | \
                       self.wq.get_board() | self.wk.get_board()
        return (1 << position) & opponent

    def is_occupied(self, square):
        occupied = self.wp.get_board() | self.bp.get_board() | self.wr.get_board() | \
                   self.br.get_board() | self.wkn.get_board() | self.bkn.get_board() | self.wb.get_board() | \
                   self.bb.get_board() | self.wq.get_board() | self.bq.get_board() | self.wk.get_board() | \
                   self.bk.get_board()
        return occupied & 1 << square

    def get_piece(self, square: Square):
        if not self.is_valid_position(square):
            return None
        for piece in self.pieces:
            if piece and piece.is_occupied(square):
                return piece
        return None

    def get_teammate(self, position, is_white):
        if not self.is_valid_position(position):
            return None
        for piece in self.pieces:
            if piece and piece.is_occupied(position) and is_white == piece.is_white():
                return piece
        return None

    def get_opponent(self, position, is_white):
        if not self.is_valid_position(position):
            return None
        for piece in self.pieces:
            if piece and piece.is_occupied(position) and not is_white == piece.is_white():
                return piece
        return None

    def is_occupied_king(self, position, is_white):
        if is_white:
            return self.wk.is_occupied(position)
        else:
            return self.bk.is_occupied(position)

    def perft(self, depth):
        if depth == 0:
            return 1
        count = 0
        for piece in self.pieces:
            if piece.is_white() == self.is_white_turn:
                moves = self.get_all_moves(piece, self.white_can_castle if self.is_white_turn
                                           else self.black_can_castle)
                for m in moves:
                    self.make_move(m)
                    count += self.perft(depth - 1)
                    self.undo_move(m)
        return count

    def make_move(self, move: Move):
        board = self.get_bb(move.piece_type, self.is_white_turn)
        board.clear_square(move.start_square)
        if move.is_capture:
            if not move.en_passant:
                move.captured = self.get_opponent(move.end_square, self.is_white_turn)
                move.captured.clear_square(move.end_square)
        if move.is_castle:
            if self.is_white_turn:
                self.white_can_castle = False, False
            else:
                self.black_can_castle = False, False
        self.update_can_castle(board, move.start_square)
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

    @staticmethod
    def reverse(bitboard):
        bitboard = ((bitboard & 0x5555555555555555) << 1) | ((bitboard >> 1) & 0x5555555555555555)
        bitboard = ((bitboard & 0x3333333333333333) << 2) | ((bitboard >> 2) & 0x3333333333333333)
        bitboard = ((bitboard & 0x0F0F0F0F0F0F0F0F) << 4) | ((bitboard >> 4) & 0x0F0F0F0F0F0F0F0F)
        bitboard = ((bitboard & 0x00FF00FF00FF00FF) << 8) | ((bitboard >> 8) & 0x00FF00FF00FF00FF)
        bitboard = ((bitboard & 0x0000FFFF0000FFFF) << 16) | ((bitboard >> 16) & 0x0000FFFF0000FFFF)
        bitboard = (bitboard << 32) | (bitboard >> 32)
        return bitboard


if __name__ == "__main__":
    chess_gui = ChessGUI()
    chess_gui.run()
    start = datetime.datetime.now()
    print(chess_gui.perft(3))
    end = datetime.datetime.now()
    print(end - start)
