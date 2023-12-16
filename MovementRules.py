from typing import List

from BitBoard import BitBoard
from Pieces import Pieces
from Move import Move


class MovementRules:

    @staticmethod
    def get_all_moves(bitboard: BitBoard, pieces, last_move: Move, can_castle) -> List[Move]:
        moves = []
        positions = MovementRules.get_positions(bitboard.get_board())
        for position in positions:
            moves.extend(MovementRules.get_moves(bitboard, position, pieces, last_move, can_castle))
        return moves

    @staticmethod
    def get_moves(bitboard: BitBoard, position, pieces, last_move: Move, can_castle) -> List[Move]:
        if bitboard.get_piece_type() == Pieces.PAWN:
            return MovementRules.get_pawn_moves(position, bitboard.is_white(), pieces, last_move)
        elif bitboard.get_piece_type() == Pieces.KNIGHT:
            return MovementRules.get_knight_moves(position, bitboard.is_white(), pieces)
        elif bitboard.get_piece_type() == Pieces.BISHOP:
            return MovementRules.get_bishop_moves(position, bitboard.is_white(), pieces)
        elif bitboard.get_piece_type() == Pieces.ROOK:
            return MovementRules.get_rook_moves(position, bitboard.is_white(), pieces, can_castle)
        elif bitboard.get_piece_type() == Pieces.QUEEN:
            return MovementRules.get_queen_moves(position, bitboard.is_white(), pieces)
        elif bitboard.get_piece_type() == Pieces.KING:
            return MovementRules.get_king_moves(position, bitboard.is_white(), pieces, can_castle)

    @classmethod
    def get_pawn_moves(cls, position, is_white, pieces, last_move: Move) -> List[Move]:
        moves = []
        direction = 1 if is_white else -1

        target_position = position + 8 * direction
        if cls.is_valid_position(target_position) and not cls.is_occupied(target_position, pieces):
            moves.append(Move(position, target_position, Pieces.PAWN))

        if (is_white and cls.get_rank(position) == 1) or (not is_white and cls.get_rank(position) == 6):
            double_jump_position = position + 16 * direction
            if cls.is_valid_position(double_jump_position) and not cls.is_occupied(double_jump_position, pieces) \
                    and not cls.is_occupied(target_position, pieces):
                moves.append(Move(position, double_jump_position, Pieces.PAWN))

        attack_left_position = position + 7 * direction
        if (
                (is_white and cls.get_file(position) > 0) or
                (not is_white and cls.get_file(position) < 7)) and \
                cls.is_valid_position(attack_left_position) and \
                cls.is_occupied_opponent(attack_left_position, is_white, pieces):
            moves.append(Move(position, attack_left_position, Pieces.PAWN, True))

        attack_right_position = position + 9 * direction
        if (
                (is_white and cls.get_file(position) < 7) or
                (not is_white and cls.get_file(position) > 0)) and \
                cls.is_valid_position(attack_right_position) and \
                cls.is_occupied_opponent(attack_right_position, is_white, pieces):
            moves.append(Move(position, attack_right_position, Pieces.PAWN, True))

        if (is_white and cls.get_rank(position) == 4) or (not is_white and cls.get_rank(position) == 3):
            moves.extend(cls.get_en_passant(position, is_white, pieces, last_move))

        return moves

    @classmethod
    def get_en_passant(cls, position, is_white, pieces, last_move: Move) -> List[Move]:
        opponent_rank = 6 if is_white else 1
        my_rank = 4 if is_white else 3
        moves = []
        if cls.get_file(position) > 0 and cls.get_rank(position) == my_rank and cls.is_occupied_opponent(position - 1,
                                                                                                         is_white,
                                                                                                         pieces):
            if cls.is_occupied_opponent(position - 1, is_white, pieces).get_piece_type() == Pieces.PAWN:
                if last_move.end_square == position - 1 and cls.get_rank(last_move.start_square) == opponent_rank:
                    if is_white:
                        moves.append(Move(position, position + 7, Pieces.PAWN, True, True))
                    else:
                        moves.append(Move(position, position - 9, Pieces.PAWN, True, True))
        if cls.get_file(position) < 7 and cls.is_occupied_opponent(position + 1, is_white, pieces):
            if cls.is_occupied_opponent(position + 1, is_white, pieces).get_piece_type() == Pieces.PAWN:
                if last_move.end_square == position + 1 and cls.get_rank(last_move.start_square) == opponent_rank:
                    if is_white:
                        moves.append(Move(position, position + 9, Pieces.PAWN, True, True))
                    else:
                        moves.append(Move(position, position - 7, Pieces.PAWN, True, True))
        return moves

    @classmethod
    def get_knight_moves(cls, position, is_white, pieces) -> List[Move]:
        moves = []
        directions = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]

        for dx, dy in directions:
            new_position = position + (dy * 8) + dx
            if (
                    cls.is_valid_position(new_position) and
                    (cls.is_occupied_opponent(new_position, is_white, pieces) or
                     not cls.is_occupied(new_position, pieces))
                    and cls.get_file(position) + dx == cls.get_file(new_position)
            ):
                moves.append(Move(position, new_position, Pieces.KNIGHT,
                                  cls.is_occupied_opponent(new_position, is_white, pieces)))

        return moves

    @classmethod
    def get_bishop_moves(cls, position, is_white, pieces) -> List[Move]:
        moves = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dx, dy in directions:
            new_position = position
            while True:
                new_position = new_position + (dy * 8) + dx
                if (dx == -1 and cls.get_file(new_position) == 7) or (dx == 1 and cls.get_file(new_position) == 0):
                    break
                elif not cls.is_valid_position(new_position):
                    break
                elif cls.is_occupied_teammate(new_position, is_white, pieces):
                    break

                is_occupied = cls.is_occupied_opponent(new_position, is_white, pieces)
                moves.append(Move(position, new_position, Pieces.BISHOP, is_occupied))
                if is_occupied:
                    break

        return moves

    @classmethod
    def get_rook_moves(cls, position, is_white, pieces, can_castle) -> List[Move]:
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in directions:
            new_position = position
            while True:
                new_position = new_position + (dy * 8) + dx
                if (dx == -1 and cls.get_file(new_position) == 7) or (dx == 1 and cls.get_file(new_position) == 0):
                    break
                elif not cls.is_valid_position(new_position):
                    break
                elif cls.is_occupied_teammate(new_position, is_white, pieces):
                    break

                is_occupied = cls.is_occupied_opponent(new_position, is_white, pieces)
                moves.append(Move(position, new_position, Pieces.ROOK, is_occupied))
                if is_occupied:
                    break
        moves.extend(cls.get_castling_moves(position, can_castle, is_white, Pieces.ROOK, pieces))

        return moves

    @classmethod
    def get_castling_moves(cls, position, can_castle, is_white, piece_type, pieces) -> List[Move]:
        moves = []
        short_castle, long_castle = can_castle
        if not (short_castle or long_castle):
            return moves

        if piece_type == Pieces.KING:
            moves.extend(cls.get_king_castling_moves(position, is_white, short_castle, long_castle, pieces))
        elif piece_type == Pieces.ROOK:
            moves.extend(cls.get_rook_castling_moves(position, is_white, short_castle, long_castle, pieces))

        return moves

    @classmethod
    def get_king_castling_moves(cls, position, is_white, short_castle, long_castle, pieces) -> List[Move]:
        moves = []
        dx = [i for i in range(1, 4)]
        if short_castle:
            if not any(cls.is_occupied(position + offset, pieces) for offset in dx[:2]):
                rook = cls.is_occupied(position + 3, pieces)
                if rook is not None and rook.get_piece_type() == Pieces.ROOK and rook.is_white() == is_white:
                    moves.append(Move(position, position + 3, Pieces.KING, is_castle=True))
        if long_castle:
            if not any(cls.is_occupied(position - offset, pieces) for offset in dx):
                rook = cls.is_occupied(position - 4, pieces)
                if rook is not None and rook.get_piece_type() == Pieces.ROOK and rook.is_white() == is_white:
                    moves.append(Move(position, position - 4, Pieces.KING, is_castle=True))
        return moves

    @classmethod
    def get_rook_castling_moves(cls, position, is_white, short_castle, long_castle, pieces) -> List[Move]:
        moves = []
        direction = 1 if cls.get_file(position) == 0 else -1 if cls.get_file(position) == 7 else 0
        dx = [position + direction * i for i in range(1, 4)]

        if direction == 1:
            if long_castle:
                if not any(cls.is_occupied(pos, pieces) for pos in dx):
                    king = cls.is_occupied(position + 4, pieces)
                    if king is not None and king.get_piece_type() == Pieces.KING and king.is_white() == is_white:
                        moves.append(Move(position, position + 4, Pieces.ROOK, is_castle=True))
        elif direction == -1:
            if short_castle:
                if not any(cls.is_occupied(pos, pieces) for pos in dx[:-1]):
                    king = cls.is_occupied(position - 3, pieces)
                    if king is not None and king.get_piece_type() == Pieces.KING and king.is_white() == is_white:
                        moves.append(Move(position, position - 3, Pieces.ROOK, is_castle=True))
        return moves

    @classmethod
    def get_queen_moves(cls, position, is_white, pieces) -> List[Move]:
        moves = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in directions:
            new_position = position
            while True:
                new_position = new_position + (dy * 8) + dx
                if (dx == -1 and cls.get_file(new_position) == 7) or (dx == 1 and cls.get_file(new_position) == 0):
                    break
                elif not cls.is_valid_position(new_position):
                    break
                elif cls.is_occupied(new_position, pieces) and not cls.is_occupied_opponent(new_position, is_white,
                                                                                            pieces):
                    break
                is_occupied = cls.is_occupied_opponent(new_position, is_white, pieces)
                moves.append(Move(position, new_position, Pieces.QUEEN, is_occupied))
                if is_occupied:
                    break

        return moves

    @classmethod
    def get_king_moves(cls, position, is_white, pieces, can_castle) -> List[Move]:
        moves = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in directions:
            new_position = position + (dy * 8) + dx
            is_occupied = cls.is_occupied_opponent(new_position, is_white, pieces)
            if (dx == -1 and cls.get_file(new_position) == 7) or (dx == 1 and cls.get_file(new_position) == 0):
                continue
            elif cls.is_valid_position(new_position) and (not cls.is_occupied(new_position, pieces) or is_occupied):
                moves.append(Move(position, new_position, Pieces.KING, is_occupied))

        moves.extend(cls.get_castling_moves(position, can_castle, is_white, Pieces.KING, pieces))
        return moves

    @classmethod
    def get_positions(cls, bitboard):
        return [position for position in range(64) if (bitboard >> position) & 1]

    @classmethod
    def is_valid_position(cls, position):
        return 0 <= position <= 63

    @classmethod
    def is_occupied(cls, position, pieces):  # returns True if any piece occupies position
        if not cls.is_valid_position(position):
            return None
        for piece in pieces:
            if piece and piece.is_occupied(position):
                return piece
        return None

    @classmethod
    def is_occupied_teammate(cls, position, is_white, pieces):
        if not cls.is_valid_position(position):
            return None
        for piece in pieces:
            if piece and piece.is_occupied(position) and is_white == piece.is_white():
                return piece
        return None

    @classmethod
    def is_occupied_opponent(cls, position, is_white, pieces):
        if not cls.is_valid_position(position):
            return None
        for piece in pieces:
            if piece and piece.is_occupied(position) and not is_white == piece.is_white():
                return piece
        return None

    @classmethod
    def is_occupied_king(cls, position, is_white, pieces):
        for piece in pieces:
            if piece.is_white() == is_white and piece.get_piece_type() == Pieces.KING:
                return piece.is_occupied(position)
        return False

    @staticmethod
    def pawn_reached_end(bitboard, position):
        return bitboard.get_piece_type() == Pieces.PAWN and \
               ((bitboard.is_white() and position >= 56) or
                (not bitboard.is_white() and position <= 7))

    @staticmethod
    def get_rank(position):
        return position // 8

    @staticmethod
    def get_file(position):
        return position % 8

    @classmethod
    def remove_check_moves(cls, piece, position, moves, king, pieces, last_move: Move, can_castle) -> List[Move]:
        filtered_moves = []
        piece.clear_square(position)
        for move in moves:
            opponent = MovementRules.is_occupied_opponent(move.end_square, piece.is_white(), pieces)
            if opponent:
                opponent.clear_square(move.end_square)
            piece.occupy_square(move.end_square)
            if not MovementRules.is_check(king, pieces, last_move, can_castle):
                filtered_moves.append(move)
            piece.clear_square(move.end_square)
            if opponent:
                opponent.occupy_square(move.end_square)
        piece.occupy_square(position)
        return filtered_moves

    @classmethod
    def is_check(cls, king: BitBoard, pieces, last_move: Move, can_castle) -> bool:
        for bitboard in pieces:
            if bitboard.is_white() != king.is_white():
                for move in cls.get_all_moves(bitboard, pieces, last_move, can_castle):
                    if move.end_square == cls.lowest_set_bit(king.get_board()):
                        return True
        return False

    @classmethod
    def lowest_set_bit(cls, n):
        return (n & -n).bit_length() - 1

    @classmethod
    def is_checkmate(cls, king, pieces, last_move: Move) -> bool:
        if not cls.is_check(king, pieces, last_move, (False, False)):
            return False
        for piece in pieces:
            if piece.is_white() == king.is_white():
                positions = MovementRules.get_positions(piece.get_board())
                for position in positions:
                    moves = MovementRules.get_moves(piece, position, pieces, last_move, (False, False))
                    piece.clear_square(position)
                    for move in moves:
                        opponent = cls.is_occupied_opponent(move.end_square, king.is_white(), pieces)
                        if opponent:
                            opponent.clear_square(move.end_square)
                        piece.occupy_square(move.end_square)
                        if not cls.is_check(king, pieces, last_move, (False, False)):
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

    @classmethod
    def is_stalemate(cls, king, pieces, last_move: Move, can_castle):
        for piece in pieces:
            if piece.is_white() == king.is_white():
                positions = MovementRules.get_positions(piece.get_board())
                for position in positions:
                    moves = cls.get_moves(piece, position, pieces, last_move, can_castle)
                    legal_moves = cls.remove_check_moves(piece, position, moves, king, pieces, last_move, can_castle)
                    if len(legal_moves) != 0:
                        return False
        return True
