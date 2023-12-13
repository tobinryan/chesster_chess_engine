import math
import pygame
import sys

from BitBoard import BitBoard
from Hashing import Hashing
from MovementRules import MovementRules
from Pieces import Pieces
from PromotionPopup import PromotionPopup


class ChessGUI:

    WIDTH, HEIGHT, SQUARE_SIZE = 800, 800, 100
    FPS = 60
    HIGHLIGHT_COLOR = (224, 244, 64, 100)

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
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Chester the Chess Engine")
        self.clock = pygame.time.Clock()
        self.selected = None  # Tuple (selected_bitboard, position)
        self.is_white_turn = True
        self.last_move = None  # Tuple (piece, start_square, dest_square, opponent_piece)
        self.fifty_move_count = 0
        self.white_can_castle = (True, True)  # Tuple (short_castle, long_castle)
        self.black_can_castle = (True, True)  # Tuple (short_castle, long_castle)
        self.Hash = Hashing(self.pieces)

    def coordinates_to_square(self, coordinates):
        """
        Converts pixel coordinates on the screen to the corresponding chess board position.

        Parameters:
        - coordinates: Tuple (x, y) representing the pixel coordinates.

        Returns:
        The chess board square as a single integer (0-63).
        """
        x, y = math.floor(coordinates[0] / self.SQUARE_SIZE), math.floor(coordinates[1] / self.SQUARE_SIZE)
        return (7 - y) * 8 + x

    def square_to_piece(self, square):
        """
        Finds the chess piece located on the given square.

        Parameters:
        - square: The index of the square (0-63).

        Returns:
        The BitBoard instance representing the piece on the square or None if the square is empty.
        """
        return MovementRules.is_occupied(square, self.pieces)

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

        for position in range(64):
            if (1 << position) & moves:
                if self.wk.is_occupied(position) or self.bk.is_occupied(position):
                    # Avoid highlighting the king's square
                    continue
                elif self.square_to_piece(position):
                    # Large circle for capturing moves
                    self.screen.blit(large_circle_box, (self.SQUARE_SIZE * (position % 8),
                                                        700 - self.SQUARE_SIZE * (position // 8)))
                else:
                    # Small circle for non-capturing moves
                    self.screen.blit(small_circle_box, (self.SQUARE_SIZE * (position % 8),
                                                        700 - self.SQUARE_SIZE * (position // 8)))

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
            piece = self.square_to_piece(i)
            if piece:
                self.screen.blit(piece.get_icon(), (self.SQUARE_SIZE * (i % 8), 700 - self.SQUARE_SIZE * (i // 8)))

    def handle_mouse_click(self, coordinates):
        """
        Handles a mouse click event on the chess board.

        Parameters:
        - coordinates: Tuple (x, y) representing the pixel coordinates of the mouse click.

        This method converts the mouse click coordinates to a square, checks the validity
        of the clicked square, and calls the appropriate method to handle the turn.
        """

        clicked_square = self.coordinates_to_square(coordinates)
        clicked_piece = self.square_to_piece(clicked_square)

        # Check if the clicked square is a valid position
        if not MovementRules.is_valid_position(clicked_square):
            return

        # Check if it's the first click and a valid piece is selected
        if self.selected is None and clicked_piece is not None:
            if self.is_white_turn != clicked_piece.is_white():
                print("Can't move enemy piece.")
                return

        # Handle the turn based on the selected piece and clicked square (source or destination)
        self.handle_turn(clicked_piece, clicked_square)

    def handle_turn(self, clicked_piece, clicked_square):
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
            moves = MovementRules.get_moves(self.selected[0], self.selected[1], self.pieces, self.last_move,
                                            (short_castle, long_castle))
            moves = MovementRules.remove_check_moves(self.selected[0], self.selected[1], moves, king, self.pieces,
                                                     self.last_move, (short_castle, long_castle))
            self.draw_board(moves)

    def handle_second_click(self, clicked_piece, clicked_square):
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
            self.selected = None
            moves = None
        elif self.square_to_piece(clicked_square) and not MovementRules.is_occupied_opponent(
                clicked_square, self.selected[0].is_white(), self.pieces) and clicked_square != self.selected[1]:
            # If the clicked square is a different friendly piece, update the selected piece and display valid moves
            self.selected = clicked_piece, clicked_square
            can_castle = self.white_can_castle if clicked_piece.is_white() else self.black_can_castle
            king = self.wk if self.is_white_turn else self.bk
            moves = MovementRules.get_moves(self.selected[0], self.selected[1], self.pieces, self.last_move, can_castle)
            moves = MovementRules.remove_check_moves(self.selected[0], self.selected[1], moves, king, self.pieces,
                                                     self.last_move, can_castle)
        else:
            # If the same piece is clicked a second time, unhighlight the piece and moves
            self.selected = None
            moves = None

        # Update the displayed board based on the updated game state
        self.draw_board(moves)

    def move_piece(self, piece_to_move, dest_square):
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

        can_castle = self.white_can_castle if piece_to_move[0].is_white() else self.black_can_castle

        # Get all possible moves for the piece and remove any that result in check
        moves = MovementRules.get_moves(piece_to_move[0], piece_to_move[1], self.pieces, self.last_move, can_castle)
        king = self.wk if self.is_white_turn else self.bk
        moves = MovementRules.remove_check_moves(piece_to_move[0], piece_to_move[1], moves, king, self.pieces,
                                                 self.last_move, can_castle)

        # Check if the destination square is a valid move
        if not self.is_valid_move(dest_square, moves):
            print("Not a valid move.")
            return False

        # Handle opponent piece if present on the destination square
        opponent_piece = MovementRules.is_occupied_opponent(dest_square, piece_to_move[0].is_white(),
                                                            self.pieces)
        self.handle_opponent_piece(opponent_piece, dest_square)

        # Handle specific piece movements (e.g. en passant, castling)
        if piece_to_move[0].get_piece_type() == Pieces.PAWN:
            self.handle_en_passant(piece_to_move[1], piece_to_move[0].is_white(), dest_square)
        elif piece_to_move[0].get_piece_type() in {Pieces.KING, Pieces.ROOK}:
            if self.handle_castling_moves(piece_to_move[0], piece_to_move[1], dest_square):
                self.fifty_move_count += 1
                return True

        # Update game state, including handling game-ending conditions
        self.fifty_move_count += 1
        self.update_can_castle(piece_to_move[0], piece_to_move[1])
        self.finalize_move(piece_to_move[0], piece_to_move[1], dest_square, opponent_piece)
        self.handle_game_state_endings()

        # Reset fifty-move count if a capture or pawn move occurs
        if opponent_piece or piece_to_move[0].get_piece_type() == Pieces.PAWN:
            self.fifty_move_count = 0

        # Update the hash value of the current game state after the move
        self.Hash.update_hash_after_move((piece_to_move[1], dest_square, piece_to_move[0].get_piece_type()),
                                         (opponent_piece.get_piece_type() if opponent_piece else None, dest_square))

        return True

    def handle_game_state_endings(self):
        """
        Handles different game state endings.

        This method checks for conditions such as checkmate, stalemate, three-move repetition,
        fifty-move rule, and insufficient material. If any of these conditions are met,
        it prints the result and exits the game.
        """
        # Check for checkmate and exit the game if found
        if MovementRules.is_checkmate(self.wk, self.pieces, self.last_move, (False, False)):
            print("Black won!")
            pygame.quit()
            sys.exit()
        elif MovementRules.is_checkmate(self.bk, self.pieces, self.last_move, (False, False)):
            print("White won!")
            pygame.quit()
            sys.exit()

        # Check for stalemate and exit the game if found
        elif MovementRules.is_stalemate(self.bk if self.is_white_turn else self.wk, self.pieces, self.last_move,
                                        (False, False)):
            print("Stalemate.")
            pygame.quit()
            sys.exit()

        # Check for three-move repetition and exit the game if found
        elif self.Hash.three_move_repetition():
            print("Draw - three move repetition.")
            pygame.quit()
            sys.exit()

        # Check for the fifty-move rule and exit the game if found
        elif self.fifty_move_count >= 100:  # checks 100 since a move is counted after both sides have moved
            print("Draw - fifty move rule.")
            pygame.quit()
            sys.exit()

        # Check for insufficient material and exit the game if found
        elif self.is_insufficient_material():
            print("Draw - insufficient material.")
            pygame.quit()
            sys.exit()

    @staticmethod
    def is_valid_move(position, moves):
        """
        Checks if a given position is a valid move.

        Parameters:
        - position: The index of the position (0-63) to check.
        - moves: A bitboard representing the available moves.

        Returns:
        True if the position is a valid move, False otherwise.
        """
        return (1 << position) & moves != 0

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
                len(MovementRules.get_positions(self.wb.get_board())) == 1
                or len(MovementRules.get_positions(self.bb.get_board())) == 1
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
                len(MovementRules.get_positions(self.wkn.get_board())) == 1
                or len(MovementRules.get_positions(self.bkn.get_board())) == 1
        )
        ):
            print("King & Knight v. King")
            return True

        # Check for King & Bishop v. King & Bishop endgame (same colored-square bishops)
        if (
                self.wkn.get_board() == 0
                and self.bkn.get_board() == 0
                and len(MovementRules.get_positions(self.wb.get_board())) == 1
                and len(MovementRules.get_positions(self.bb.get_board())) == 1
                and self.get_square_color(MovementRules.get_positions(self.wb.get_board())[0])
                == self.get_square_color(MovementRules.get_positions(self.bb.get_board())[0])
        ):
            print("king and bishop vs king and bishop")
            return True
        return False

    @staticmethod
    def get_square_color(position):
        """
        Determines the color of a chessboard square based on its position.

        Parameters:
        - position: The index of the square (0-63).

        Returns:
        True if the square is dark, False if the square is light.
        """
        return (MovementRules.get_file(position) + MovementRules.get_rank(position)) % 2 == 0

    @staticmethod
    def handle_opponent_piece(piece, position):
        """
        Handles the removal of an opponent's piece from the board.

        Parameters:
        - piece: The opponent's piece to be removed.
        - position: The index of the square where the opponent's piece is located.

        This method clears the square on the board occupied by the opponent's piece.
        """
        if piece:
            print("Took opponent piece {}.".format(piece.get_piece_type()))
            piece.clear_square(position)

    def handle_en_passant(self, start_square, is_white, dest_square):
        """
        Handles en passant captures.

        Parameters:
        - start_square: The index of the current position of the pawn.
        - is_white: True if the pawn is white, False if black.
        - dest_square: The index of the destination square of the pawn.

        This method checks for en passant captures and removes the captured opponent's pawn.
        """

        # Get en passant moves for the current pawn
        en_passant_moves = MovementRules.get_en_passant(start_square, is_white, self.pieces, self.last_move)

        # Check if the destination square is an en passant capture
        if (1 << dest_square) and en_passant_moves:
            direction = -1 if is_white else 1

            # Find and clear the square of the captured opponent's pawn
            opponent_position = dest_square + 8 * direction
            opponent_piece = MovementRules.is_occupied_opponent(opponent_position, is_white, self.pieces)
            if opponent_piece:
                opponent_piece.clear_square(opponent_position)
            else:
                raise Exception("Completed en passant move but couldn't find opponent piece.")

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
        castling_moves = MovementRules.get_castling_moves(
            start_square, can_castle, piece.is_white(), piece.get_piece_type(), self.pieces
        )

        # Check if the next position is a valid castling move
        if (1 << dest_square) & castling_moves:
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
        other_piece = self.square_to_piece(dest_square)
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

    def finalize_move(self, piece, start_square, dest_square, opponent_piece):
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
        self.update_can_castle(piece, start_square)

        # Clear the current square and occupy the destination square with the piece
        piece.clear_square(start_square)
        piece.occupy_square(dest_square)

        # Check for pawn promotion
        if MovementRules.pawn_reached_end(piece, dest_square):
            self.promote_pawn(piece, dest_square)

        # Store information about the last move
        self.last_move = (piece, start_square, dest_square, opponent_piece)

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
                if MovementRules.get_file(square) == 0:
                    self.white_can_castle = self.white_can_castle[0], False
                elif MovementRules.get_file(square) == 7:
                    self.white_can_castle = False, self.white_can_castle[1]

        # Update castling flags for black player
        if self.black_can_castle:
            if not piece.is_white() and piece.get_piece_type() == Pieces.KING:
                self.white_can_castle = False, False
            elif not piece.is_white() and piece.get_piece_type() == Pieces.ROOK:
                if MovementRules.get_file(square) == 0:
                    self.black_can_castle = self.black_can_castle[0], False
                elif MovementRules.get_file(square) == 7:
                    self.black_can_castle = False, self.black_can_castle[1]

    def promote_pawn(self, bitboard, square):
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


if __name__ == "__main__":
    chess_gui = ChessGUI()
    chess_gui.run()
