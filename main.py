import math

import pygame
import sys

from BitBoard import BitBoard
from Move import Move
from Pieces import Pieces
from Board import Board
from PromotionPopup import PromotionPopup


class ChessGUI:
    WIDTH, HEIGHT, SQUARE_SIZE = 800, 800, 100
    FPS = 60
    HIGHLIGHT_COLOR = (224, 244, 64, 100)
    Square = int

    board_img = pygame.image.load('images/board.png')

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Chester the Chess Engine")
        self.clock = pygame.time.Clock()

        pygame.mixer.init()
        self.capture_sound = pygame.mixer.Sound("sounds/capture.ogg")
        self.castle_sound = pygame.mixer.Sound("sounds/castle.ogg")
        self.check_sound = pygame.mixer.Sound("sounds/move-check.ogg")
        self.move_sound = pygame.mixer.Sound("sounds/move-self.ogg")
        self.promote_sound = pygame.mixer.Sound("sounds/promote.ogg")

        self.board = Board(self)

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
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_z:
                        self.board.undo_move(self.board.last_move)
                        self.draw_board(None)

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
        self.screen.blit(highlighted_box, (self.SQUARE_SIZE * (self.board.selected[1] % 8),
                                           700 - self.SQUARE_SIZE * (self.board.selected[1] // 8)))

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
            if self.board.wk.is_occupied(move.end_square) or self.board.bk.is_occupied(move.end_square):
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
        self.screen.blit(self.board_img, (0, 0))

        # Draw a highlighted box around the selected piece (if any)
        if self.board.selected is not None:
            self.draw_highlighted_piece()

        # Draw circles to highlight valid moves (if provided)
        if moves is not None:
            self.draw_moves(moves)

        # Draw pieces on the board
        for i in range(64):
            piece = self.get_piece(i)
            if piece:
                self.screen.blit(piece.get_icon(), (self.SQUARE_SIZE * (i % 8), 700 - self.SQUARE_SIZE * (i // 8)))

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
        if not self.board.is_valid_square(clicked_square):
            return

        # Check if it's the first click and a valid piece is selected
        if self.board.selected is None and clicked_piece is not None:
            if self.board.is_white_turn != clicked_piece.is_white():
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

        if self.board.selected:
            # If a piece is already selected, handle the second click
            self.handle_second_click(clicked_piece, clicked_square)
        elif clicked_piece:
            # If no piece is selected, set the selected piece and display valid moves
            self.board.selected = clicked_piece, clicked_square

            # Determine available moves based on the selected piece and update the displayed board
            short_castle, long_castle = self.board.white_can_castle if self.board.selected[
                0].is_white() else self.board.black_can_castle
            king = self.board.wk if self.board.is_white_turn else self.board.bk
            moves = self.board.get_moves(self.board.selected[0], self.board.selected[1], (short_castle, long_castle))
            moves = self.board.remove_check_moves(self.board.selected[0], self.board.selected[1], moves, king)
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
        if self.board.move(self.board.selected, clicked_square):
            # If the move is successful, toggle the turn and reset the selected piece
            self.board.is_white_turn = not self.board.is_white_turn
            print(self.move_notation())
            self.sound()
            self.board.selected = None
            moves = None
        elif self.get_piece(clicked_square) and not \
                self.board.get_opponent(clicked_square, self.board.selected[0].is_white()) \
                and clicked_square != self.board.selected[1]:
            # If the clicked square is a different friendly piece, update the selected piece and display valid moves
            self.board.selected = clicked_piece, clicked_square
            can_castle = self.board.white_can_castle if clicked_piece.is_white() else self.board.black_can_castle
            king = self.board.wk if self.board.is_white_turn else self.board.bk
            moves = self.board.get_moves(clicked_piece, clicked_square, can_castle)
            moves = self.board.remove_check_moves(clicked_piece, clicked_square, moves, king)
        else:
            # If the same piece is clicked a second time, unhighlight the piece and moves
            self.board.selected = None
            moves = None

        # Update the displayed board based on the updated game state
        self.draw_board(moves)

    def sound(self):
        move = self.board.last_move
        if move.is_castle:
            pygame.mixer.Sound.play(self.castle_sound)
        elif move.is_capture:
            pygame.mixer.Sound.play(self.capture_sound)
        elif move.is_promotion:
            pygame.mixer.Sound.play(self.promote_sound)
        elif self.board.is_check(self.board.wk if self.board.is_white_turn else self.board.bk):
            pygame.mixer.Sound.play(self.check_sound)
        else:
            pygame.mixer.Sound.play(self.move_sound)

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
        promotion_popup = PromotionPopup(self.screen, [piece for piece in self.board.pieces if
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
                        promotion_choice.occupy_square(square)
                        return

            promotion_popup.draw()
            pygame.display.flip()

    def import_fen(self, fen: str):
        for piece in self.board.pieces:
            piece.clear_board()
        self.board.white_can_castle = (False, False)
        self.board.black_can_castle = (False, False)

        curr_char = 0
        board_idx = 56
        while fen[curr_char] != ' ':
            match fen[curr_char]:
                case 'P':
                    self.board.wp.occupy_square(board_idx)
                    board_idx += 1
                case 'p':
                    self.board.bp.occupy_square(board_idx)
                    board_idx += 1
                case 'N':
                    self.board.wkn.occupy_square(board_idx)
                    board_idx += 1
                case 'n':
                    self.board.bkn.occupy_square(board_idx)
                    board_idx += 1
                case 'R':
                    self.board.wr.occupy_square(board_idx)
                    board_idx += 1
                case 'r':
                    self.board.br.occupy_square(board_idx)
                    board_idx += 1
                case 'B':
                    self.board.wb.occupy_square(board_idx)
                    board_idx += 1
                case 'b':
                    self.board.bb.occupy_square(board_idx)
                    board_idx += 1
                case 'Q':
                    self.board.wq.occupy_square(board_idx)
                    board_idx += 1
                case 'q':
                    self.board.bq.occupy_square(board_idx)
                    board_idx += 1
                case 'K':
                    self.board.wk.occupy_square(board_idx)
                    board_idx += 1
                case 'k':
                    self.board.bk.occupy_square(board_idx)
                    board_idx += 1
                case '/':
                    board_idx -= 16
                case '1':
                    board_idx += 1
                case '2':
                    board_idx += 2
                case '3':
                    board_idx += 3
                case '4':
                    board_idx += 4
                case '5':
                    board_idx += 5
                case '6':
                    board_idx += 6
                case '7':
                    board_idx += 7
                case '8':
                    board_idx += 8
            curr_char += 1

        curr_char += 1
        self.board.is_white_turn = fen[curr_char] == 'w'
        curr_char += 2
        while fen[curr_char] != ' ':
            match fen[curr_char]:
                case '-':
                    curr_char += 1
                case 'K':
                    self.board.white_can_castle = (True, self.board.white_can_castle[1])
                case 'Q':
                    self.board.white_can_castle = (self.board.white_can_castle[0], True)
                case 'k':
                    self.board.black_can_castle = (True, self.board.black_can_castle[1])
                case 'q':
                    self.board.black_can_castle = (self.board.black_can_castle[0], True)
            curr_char += 1

        curr_char += 1
        if fen[curr_char] != '-':
            file = fen[curr_char].lower()
            file_idx = ord(file) - ord('a')
            if self.board.is_white_turn:
                self.board.last_move = Move(48 + file_idx, 32 + file_idx, Pieces.PAWN)
            else:
                self.board.last_move = Move(8 + file_idx, 24 + file_idx, Pieces.PAWN)

    def move_notation(self):
        move = ""
        if self.board.last_move:
            piece = self.board.PIECE_SYMBOLS[self.board.last_move.piece_type]
            piece = self.board.UNICODE_PIECE_SYMBOLS[piece if self.board.is_white_turn else piece.upper()]
            move += piece
            if self.board.last_move.is_capture and self.board.last_move.piece_type == Pieces.PAWN or \
                    self.board.last_move.en_passant:
                move += self.board.FILE_NAMES[self.board.get_file(self.board.last_move.start_square)] + "x"
            elif self.board.last_move.is_capture:
                move += "x"
            move += self.board.square_name(self.board.last_move.end_square)
        return move

    def algebraic_notation(self, move: Move):
        return self.board.square_name(move.start_square) + self.board.square_name(move.end_square)

    def get_piece(self, square: Square):
        if not self.board.is_valid_square(square):
            return None
        for piece in self.board.pieces:
            if piece and piece.is_occupied(square):
                return piece
        return None

if __name__ == "__main__":
    chess_gui = ChessGUI()
    chess_gui.import_fen("r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - ")
    chess_gui.run()
