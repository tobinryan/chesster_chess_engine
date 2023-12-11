import math

import pygame
import sys

from BitBoard import BitBoard
from MovementRules import MovementRules
from Hashing import Hashing
from Pieces import Pieces
from PromotionPopup import PromotionPopup


class ChessGUI:
    pygame.init()

    WIDTH, HEIGHT, SQUARE_SIZE = 800, 800, 100
    FPS = 60
    HIGHLIGHT_COLOR = (224, 244, 64, 100)

    board = pygame.image.load('images/board.png')

    wp = BitBoard(0b11111111 << 8, pygame.image.load('images/wp.png'), True, Pieces.PAWN)
    bp = BitBoard(0b11111111 << 48, pygame.image.load('images/bp.png'), False, Pieces.PAWN)
    wr = BitBoard(0b10000001, pygame.image.load('images/wr.png'), True, Pieces.ROOK)
    br = BitBoard(0b10000001 << 56, pygame.image.load('images/br.png'), False, Pieces.ROOK)
    wkn = BitBoard(0b01000010, pygame.image.load('images/wkn.png'), True, Pieces.KNIGHT)
    bkn = BitBoard(0b01000010 << 56, pygame.image.load('images/bkn.png'), False, Pieces.KNIGHT)
    wb = BitBoard(0b00100100, pygame.image.load('images/wb.png'), True, Pieces.BISHOP)
    bb = BitBoard(0b00100100 << 56, pygame.image.load('images/bb.png'), False, Pieces.BISHOP)
    wq = BitBoard(0b00001000, pygame.image.load('images/wq.png'), True, Pieces.QUEEN)
    bq = BitBoard(0b00001000 << 56, pygame.image.load('images/bq.png'), False, Pieces.QUEEN)
    wk = BitBoard(0b00010000, pygame.image.load('images/wk.png'), True, Pieces.KING)
    bk = BitBoard(0b00010000 << 56, pygame.image.load('images/bk.png'), False, Pieces.KING)
    pieces = [wp, bp, wr, br, wkn, bkn, wb, bb, wq, bq, wk, bk]

    def __init__(self):
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Chesster the Chess Engine")
        self.clock = pygame.time.Clock()
        self.selected = None
        self.is_white_turn = True
        self.last_move = None
        self.fifty_move_count = 0
        self.white_can_castle = (True, True)  # (short_castle, long_castle)
        self.black_can_castle = (True, True)  # (short_castle, long_castle)
        self.Hash = Hashing(self.pieces)

    @staticmethod
    def coordinates_to_position(coordinates):
        x, y = math.floor(coordinates[0] / 100), math.floor(coordinates[1] / 100)
        return (7 - y) * 8 + x

    def square_to_piece(self, square):
        for piece in self.pieces:
            if piece.get_board() & (1 << square):
                return piece
        return None

    def run(self):
        running = True
        self.draw_board(None)
        while running:
            self.clock.tick(self.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_click(pygame.mouse.get_pos())

            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def draw_highlighted_piece(self):
        highlighted_box = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE), pygame.SRCALPHA)
        highlighted_box.fill(self.HIGHLIGHT_COLOR)
        self.screen.blit(highlighted_box, (self.SQUARE_SIZE * (self.selected[1] % 8),
                                           700 - self.SQUARE_SIZE * (self.selected[1] // 8)))

    def draw_moves(self, moves):
        small_circle_box = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(small_circle_box, (0, 0, 0, 32), (self.SQUARE_SIZE // 2, self.SQUARE_SIZE // 2), 20)
        large_circle_box = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(large_circle_box, (0, 0, 0, 32), (self.SQUARE_SIZE // 2, self.SQUARE_SIZE // 2), 50, 10)
        for position in range(64):
            if (1 << position) & moves:
                if self.wk.get_board() & (1 << position) or self.bk.get_board() & (1 << position):
                    continue
                elif MovementRules.is_occupied(position, self.pieces):
                    self.screen.blit(large_circle_box, (self.SQUARE_SIZE * (position % 8),
                                                        700 - self.SQUARE_SIZE * (position // 8)))
                else:
                    self.screen.blit(small_circle_box, (self.SQUARE_SIZE * (position % 8),
                                                        700 - self.SQUARE_SIZE * (position // 8)))

    def draw_board(self, moves):
        self.screen.blit(self.board, (0, 0))

        if self.selected is not None:
            self.draw_highlighted_piece()

        if moves is not None:
            self.draw_moves(moves)

        for i in range(64):
            if self.wp.is_occupied(i):
                self.screen.blit(self.wp.get_icon(), (self.SQUARE_SIZE * (i % 8), 700 - self.SQUARE_SIZE * (i // 8)))
            elif self.bp.is_occupied(i):
                self.screen.blit(self.bp.get_icon(), (self.SQUARE_SIZE * (i % 8), 700 - self.SQUARE_SIZE * (i // 8)))
            elif self.wr.is_occupied(i):
                self.screen.blit(self.wr.get_icon(), (self.SQUARE_SIZE * (i % 8), 700 - self.SQUARE_SIZE * (i // 8)))
            elif self.br.is_occupied(i):
                self.screen.blit(self.br.get_icon(), (self.SQUARE_SIZE * (i % 8), 700 - self.SQUARE_SIZE * (i // 8)))
            elif self.wkn.is_occupied(i):
                self.screen.blit(self.wkn.get_icon(), (self.SQUARE_SIZE * (i % 8), 700 - self.SQUARE_SIZE * (i // 8)))
            elif self.bkn.is_occupied(i):
                self.screen.blit(self.bkn.get_icon(), (self.SQUARE_SIZE * (i % 8), 700 - self.SQUARE_SIZE * (i // 8)))
            elif self.wb.is_occupied(i):
                self.screen.blit(self.wb.get_icon(), (self.SQUARE_SIZE * (i % 8), 700 - self.SQUARE_SIZE * (i // 8)))
            elif self.bb.is_occupied(i):
                self.screen.blit(self.bb.get_icon(), (self.SQUARE_SIZE * (i % 8), 700 - self.SQUARE_SIZE * (i // 8)))
            elif self.wq.is_occupied(i):
                self.screen.blit(self.wq.get_icon(), (self.SQUARE_SIZE * (i % 8), 700 - self.SQUARE_SIZE * (i // 8)))
            elif self.bq.is_occupied(i):
                self.screen.blit(self.bq.get_icon(), (self.SQUARE_SIZE * (i % 8), 700 - self.SQUARE_SIZE * (i // 8)))
            elif self.wk.is_occupied(i):
                self.screen.blit(self.wk.get_icon(), (self.SQUARE_SIZE * (i % 8), 700 - self.SQUARE_SIZE * (i // 8)))
            elif self.bk.is_occupied(i):
                self.screen.blit(self.bk.get_icon(), (self.SQUARE_SIZE * (i % 8), 700 - self.SQUARE_SIZE * (i // 8)))

    def handle_mouse_click(self, coordinates):
        clicked_position = self.coordinates_to_position(coordinates)
        clicked_piece = self.square_to_piece(clicked_position)

        if not MovementRules.is_valid_position(clicked_position):
            return
        # if self.selected is None and clicked_piece is not None:
        #     if (self.is_white_turn and not clicked_piece.is_white()) or \
        #             (not self.is_white_turn and clicked_piece.is_white()):
        #         print("Can't move enemy piece.")
        #         return

        if self.is_white_turn:
            self.handle_white_turn(clicked_piece, clicked_position)
        else:
            # TODO: Add chess engine logic for black's turn
            self.handle_white_turn(clicked_piece, clicked_position)

    def handle_white_turn(self, clicked_piece, clicked_position):
        if self.selected:
            self.handle_second_click(clicked_piece, clicked_position)
        elif clicked_piece:
            self.selected = clicked_piece, clicked_position
            short_castle, long_castle = self.white_can_castle if self.selected[0].is_white() else self.black_can_castle
            moves = MovementRules.get_moves(self.selected[0], self.selected[1], self.pieces, self.last_move,
                                            (short_castle, long_castle))
            king = self.wk if self.is_white_turn else self.bk
            moves = MovementRules.remove_check_moves(self.selected[0], self.selected[1], moves, king, self.pieces,
                                                     self.last_move, (short_castle, long_castle))
            self.draw_board(moves)

    def handle_second_click(self, clicked_piece, clicked_position):
        if self.move_piece(self.selected, clicked_position):
            self.is_white_turn = not self.is_white_turn
            self.selected = None
            moves = None
        elif MovementRules.is_occupied(clicked_position, self.pieces) and not MovementRules.is_occupied_opponent(
                clicked_position, self.selected[0].is_white(), self.pieces) and clicked_position != self.selected[1]:
            self.selected = clicked_piece, clicked_position
            can_castle = self.white_can_castle if clicked_piece.is_white() else self.black_can_castle
            moves = MovementRules.get_moves(self.selected[0], self.selected[1], self.pieces, self.last_move, can_castle)
            king = self.wk if self.is_white_turn else self.bk
            moves = MovementRules.remove_check_moves(self.selected[0], self.selected[1], moves, king, self.pieces,
                                                     self.last_move, can_castle)
        else:
            self.selected = None
            moves = None

        self.draw_board(moves)

    def move_piece(self, piece_to_move, clicked_position):
        can_castle = self.white_can_castle if piece_to_move[0].is_white() else self.black_can_castle
        moves = MovementRules.get_moves(piece_to_move[0], piece_to_move[1], self.pieces, self.last_move, can_castle)
        king = self.wk if self.is_white_turn else self.bk
        moves = MovementRules.remove_check_moves(piece_to_move[0], piece_to_move[1], moves, king, self.pieces,
                                                 self.last_move, can_castle)
        self.draw_board(moves)
        if not self.is_valid_move(clicked_position, moves):
            print("Not a valid move.")
            return False

        opponent_piece = MovementRules.is_occupied_opponent(clicked_position, piece_to_move[0].is_white(),
                                                            self.pieces)
        self.handle_opponent_piece(opponent_piece, clicked_position)

        if piece_to_move[0].get_piece_type() == Pieces.PAWN:
            self.handle_pawn_moves(piece_to_move[1], piece_to_move[0].is_white(), clicked_position)
        elif piece_to_move[0].get_piece_type() in {Pieces.KING, Pieces.ROOK}:
            if self.handle_castling_moves(piece_to_move[0], piece_to_move[1], clicked_position):
                self.fifty_move_count += 1
                return True

        self.fifty_move_count += 1
        self.handle_game_state_endings()
        self.update_can_castle(piece_to_move[0], piece_to_move[1])
        self.handle_last_move(piece_to_move[0], piece_to_move[1], clicked_position, opponent_piece)
        if opponent_piece or piece_to_move[0].get_piece_type() == Pieces.PAWN:
            self.fifty_move_count = 0

        opp_piece_type = opponent_piece.get_piece_type() if opponent_piece is not None else None
        self.Hash.update_hash_after_move((piece_to_move[1], clicked_position, piece_to_move[0].get_piece_type()),
                                         (opp_piece_type, clicked_position))

        return True

    def handle_game_state_endings(self):
        if MovementRules.is_checkmate(self.wk, self.pieces, self.last_move, (False, False)):
            print("Black won!")
            pygame.quit()
            sys.exit()
        elif MovementRules.is_checkmate(self.bk, self.pieces, self.last_move, (False, False)):
            print("White won!")
            pygame.quit()
            sys.exit()

        elif MovementRules.is_stalemate(self.bk if self.is_white_turn else self.wk, self.pieces, self.last_move,
                                        (False, False)):
            print("Stalemate.")
            pygame.quit()
            sys.exit()
        elif self.Hash.three_move_repetition():
            print("Draw - three move repetition.")
            pygame.quit()
            sys.exit()
        elif self.fifty_move_count >= 100:
            print("Draw - fifty move rule.")
            pygame.quit()
            sys.exit()
        elif self.is_insufficient_material():
            print("Draw - insufficient material.")
            pygame.quit()
            sys.exit()

    @staticmethod
    def is_valid_move(position, moves):
        if not (1 << position) & moves:
            return False
        return True

    def is_insufficient_material(self):  # king, bishop
        if self.wp.get_board() != 0 or self.bp.get_board() != 0 or \
                self.wq.get_board() != 0 or self.bq.get_board() != 0 or \
                self.wr.get_board() != 0 or self.br.get_board() != 0:
            return False
        if self.wb.get_board() == 0 and self.bb.get_board() == 0 and \
                self.wkn.get_board() == 0 and self.bkn.get_board() == 0:
            print("king V king")
            return True
        if self.wkn.get_board() == 0 and self.bkn.get_board() == 0 and \
                (self.wb.get_board() == 0 or self.bb.get_board() == 0) and \
                (len(MovementRules.get_set_bits(self.wb.get_board())) == 1 or
                 len(MovementRules.get_set_bits(self.bb.get_board()) == 1)):
            print("king and bishop vs king")
            return True
        if self.wb.get_board() == 0 and self.bb.get_board() == 0 and \
                (self.wkn.get_board() == 0 or self.bkn.get_board() == 0) and \
                (len(MovementRules.get_positions(self.wkn.get_board())) == 1 or
                 len(MovementRules.get_positions(self.bkn.get_board())) == 1):
            print("king and knight vs king")
            return True
        if self.wkn.get_board() == 0 and self.bkn.get_board() == 0 and \
                len(MovementRules.get_set_bits(self.wb.get_board())) == 1 and \
                len(MovementRules.get_set_bits(self.bb.get_board())) == 1 and \
                self.get_square_color(MovementRules.get_positions(self.wb.get_board())[0]) == \
                self.get_square_color(MovementRules.get_positions(self.bb.get_board())[0]):
            print("king and bishop vs king and bishop")
            return True
        return False

    def get_square_color(self, position): # true = dark, false = light
        return (MovementRules.get_file(position) + MovementRules.get_rank(position)) % 2 == 0

    @staticmethod
    def handle_opponent_piece(piece, position):
        if piece:
            print("Took opponent piece {}.".format(piece.get_piece_type()))
            piece.clear_square(position)

    def handle_pawn_moves(self, current_position, is_white, next_position):
        en_passant_moves = MovementRules.get_en_passant(current_position, is_white, self.pieces, self.last_move)
        if (1 << next_position) and en_passant_moves:
            direction = -1 if is_white else 1
            opponent_piece = MovementRules.is_occupied_opponent(next_position + 8 * direction, is_white, self.pieces)
            opponent_piece.clear_square(next_position + 8 * direction)

    def handle_castling_moves(self, piece, current_position, next_position):
        can_castle = self.white_can_castle if piece.is_white() else self.black_can_castle
        castling_moves = MovementRules.get_castling_moves(current_position, can_castle, piece.is_white(),
                                                          piece.get_piece_type(), self.pieces)
        if (1 << next_position) & castling_moves:
            self.perform_castling(piece, current_position, next_position)
            return True
        return False

    def perform_castling(self, piece, current_position, next_position):
        if piece.is_white():
            self.white_can_castle = False, False
        else:
            self.black_can_castle = False, False
        if piece.get_piece_type() == Pieces.ROOK:
            rook_dx = 3 if current_position < next_position else -2
            king_dx = -2 if current_position < next_position else 2
        else:
            rook_dx = -2 if current_position < next_position else 3
            king_dx = 2 if current_position < next_position else -2

        piece.clear_square(current_position)
        if piece.get_piece_type() == Pieces.KING:
            piece.occupy_square(current_position + king_dx)
        else:
            piece.occupy_square(current_position + rook_dx)
        other_piece = MovementRules.is_occupied(next_position, self.pieces)
        other_piece.clear_square(next_position)
        if other_piece.get_piece_type() == Pieces.KING:
            other_piece.occupy_square(next_position + king_dx)
        else:
            other_piece.occupy_square(next_position + rook_dx)
        return True

    def handle_last_move(self, piece, current_position, clicked_position, opponent_piece):
        self.update_can_castle(piece, current_position)
        piece.clear_square(current_position)
        piece.occupy_square(clicked_position)

        if MovementRules.pawn_reached_end(piece, clicked_position):
            self.promote_pawn(piece, clicked_position)

        self.last_move = (piece, current_position, clicked_position, opponent_piece)

    def update_can_castle(self, piece, position):
        if self.white_can_castle:
            if piece.is_white() and piece.get_piece_type() == Pieces.KING:
                self.white_can_castle = False, False
            elif piece.is_white() and piece.get_piece_type() == Pieces.ROOK:
                if MovementRules.get_file(position) == 0:
                    self.white_can_castle = self.white_can_castle[0], False
                elif MovementRules.get_file(position) == 7:
                    self.white_can_castle = False, self.white_can_castle[1]
        if self.black_can_castle:
            if not piece.is_white() and piece.get_piece_type() == Pieces.KING:
                self.white_can_castle = False, False
            elif not piece.is_white() and piece.get_piece_type() == Pieces.ROOK:
                if MovementRules.get_file(position) == 0:
                    self.black_can_castle = self.black_can_castle[0], False
                elif MovementRules.get_file(position) == 7:
                    self.black_can_castle = False, self.black_can_castle[1]

    def promote_pawn(self, bitboard, position):
        bitboard.clear_square(position)
        promotion_popup = PromotionPopup(self.screen, [piece for piece in self.pieces if
                                                       piece.is_white() == bitboard.is_white()])
        promotion_popup.draw()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    click_position = pygame.mouse.get_pos()
                    promotion_choice = promotion_popup.handle_click(click_position)
                    if promotion_choice:
                        self.handle_promotion_choice(position, bitboard.is_white(), promotion_choice)
                        return

            promotion_popup.draw()
            pygame.display.flip()

    def handle_promotion_choice(self, position, is_white, promotion_choice):
        for piece in self.pieces:
            if piece.get_piece_type() == promotion_choice and piece.is_white() == is_white:
                piece.occupy_square(position)


if __name__ == "__main__":
    chess_gui = ChessGUI()
    chess_gui.run()
