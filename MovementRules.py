from Pieces import Pieces


class MovementRules:

    @staticmethod
    def get_all_moves(bitboard, pieces, last_move, can_castle):
        moves = 0
        positions = MovementRules.get_positions(bitboard.get_board())
        for position in positions:
            moves |= MovementRules.get_moves(bitboard, position, pieces, last_move, can_castle)
        return moves

    @staticmethod
    def get_moves(bitboard, position, pieces, last_move, can_castle):
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
    def get_pawn_moves(cls, position, is_white, pieces, last_move):
        moves = 0
        direction = 1 if is_white else -1

        target_position = position + 8 * direction
        if cls.is_valid_position(target_position) and not cls.is_occupied(target_position, pieces):
            moves |= 1 << target_position

        if (is_white and cls.get_rank(position) == 1) or (not is_white and cls.get_rank(position) == 6):
            double_jump_position = position + 16 * direction
            if cls.is_valid_position(double_jump_position) and not cls.is_occupied(double_jump_position, pieces) \
                    and not cls.is_occupied(target_position, pieces):
                moves |= 1 << double_jump_position

        attack_left_position = position + 7 * direction
        if ((is_white and cls.get_file(position) > 0) or (not is_white and cls.get_file(position) < 7)) and \
                cls.is_valid_position(attack_left_position) and cls.is_occupied_opponent(
            attack_left_position, is_white, pieces):
            moves |= 1 << attack_left_position

        attack_right_position = position + 9 * direction
        if ((is_white and cls.get_file(position) < 7) or (not is_white and cls.get_file(position) > 0)) and \
                cls.is_valid_position(attack_right_position) and cls.is_occupied_opponent(attack_right_position,
                                                                                          is_white, pieces):
            moves |= 1 << attack_right_position

        if (is_white and cls.get_rank(position) == 4) or (not is_white and cls.get_rank(position) == 3):
            moves |= cls.get_en_passant(position, is_white, pieces, last_move)

        return moves

    @classmethod
    def get_en_passant(cls, position, is_white, pieces, last_move):
        opponent_rank = 6 if is_white else 1
        my_rank = 4 if is_white else 3
        moves = 0
        if cls.get_file(position) > 0 and cls.get_rank(position) == my_rank and cls.is_occupied_opponent(position - 1,
                                                                                                         is_white,
                                                                                                         pieces):
            if cls.is_occupied_opponent(position - 1, is_white, pieces).get_piece_type() == Pieces.PAWN:
                if last_move[2] == position - 1 and cls.get_rank(last_move[1]) == opponent_rank:
                    if is_white:
                        moves |= 1 << (position + 7)
                    else:
                        moves |= 1 << (position - 9)
        if cls.get_file(position) < 7 and cls.is_occupied_opponent(position + 1, is_white, pieces):
            if cls.is_occupied_opponent(position + 1, is_white, pieces).get_piece_type() == Pieces.PAWN:
                if last_move[2] == position + 1 and cls.get_rank(last_move[1]) == opponent_rank:
                    if is_white:
                        moves |= 1 << (position + 9)
                    else:
                        moves |= 1 << (position - 7)
        return moves

    @classmethod
    def get_knight_moves(cls, position, is_white, pieces):
        moves = 0
        directions = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]

        for dx, dy in directions:
            new_position = position + (dy * 8) + dx
            if (
                    cls.is_valid_position(new_position) and
                    (cls.is_occupied_opponent(new_position, is_white, pieces) or
                     not cls.is_occupied(new_position, pieces))
                    and cls.get_file(position) + dx == cls.get_file(new_position)
            ):
                moves |= 1 << new_position

        return moves

    @classmethod
    def get_bishop_moves(cls, position, is_white, pieces):
        moves = 0
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

                moves |= (1 << new_position)
                if cls.is_occupied_opponent(new_position, is_white, pieces):
                    break

        return moves

    @classmethod
    def get_rook_moves(cls, position, is_white, pieces, can_castle):
        moves = 0
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

                moves |= (1 << new_position)
                if cls.is_occupied_opponent(new_position, is_white, pieces):
                    break
        moves |= cls.get_castling_moves(position, can_castle, is_white, Pieces.ROOK, pieces)

        return moves

    @classmethod
    def get_castling_moves(cls, position, can_castle, is_white, piece_type, pieces):
        moves = 0
        if not can_castle:
            return moves

        if piece_type == Pieces.KING:
            moves |= cls.get_king_castling_moves(position, is_white, pieces)
        elif piece_type == Pieces.ROOK:
            moves |= cls.get_rook_castling_moves(position, is_white, pieces)

        return moves

    @classmethod
    def get_king_castling_moves(cls, position, is_white, pieces):
        moves = 0
        dx = [i for i in range(1, 4)]
        if not any(cls.is_occupied(position + offset, pieces) for offset in dx[:2]):
            rook = cls.is_occupied(position + 3, pieces)
            if rook is not None and rook.get_piece_type() == Pieces.ROOK and rook.is_white() == is_white:
                moves |= 1 << (position + 3)
        if not any(cls.is_occupied(position - offset, pieces) for offset in dx):
            rook = cls.is_occupied(position - 4, pieces)
            if rook is not None and rook.get_piece_type() == Pieces.ROOK and rook.is_white() == is_white:
                moves |= 1 << (position - 4)
        return moves

    @classmethod
    def get_rook_castling_moves(cls, position, is_white, pieces):
        moves = 0
        direction = 1 if cls.get_file(position) == 0 else -1
        dx = [position + direction * i for i in range(1, 4)]

        if direction == 1:
            if not any(cls.is_occupied(pos, pieces) for pos in dx):
                king = cls.is_occupied(position + 4, pieces)
                if king is not None and king.get_piece_type() == Pieces.KING and king.is_white() == is_white:
                    moves |= 1 << (position + 4)
        else:
            if not any(cls.is_occupied(pos, pieces) for pos in dx[:-1]):
                king = cls.is_occupied(position - 3, pieces)
                if king is not None and king.get_piece_type() == Pieces.KING and king.is_white() == is_white:
                    moves |= 1 << (position - 3)
        return moves

    @classmethod
    def get_queen_moves(cls, position, is_white, pieces):
        moves = 0
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

                moves |= (1 << new_position)
                if cls.is_occupied_opponent(new_position, is_white, pieces):
                    break

        return moves

    @classmethod
    def get_king_moves(cls, position, is_white, pieces, can_castle):
        moves = 0
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in directions:
            new_position = position + (dy * 8) + dx
            if (dx == -1 and cls.get_file(new_position) == 7) or (dx == 1 and cls.get_file(new_position) == 0):
                continue
            elif cls.is_valid_position(new_position) and (not cls.is_occupied(new_position, pieces) or
                                                          cls.is_occupied_opponent(new_position, is_white, pieces)):
                moves |= (1 << new_position)

        moves |= cls.get_castling_moves(position, can_castle, is_white, Pieces.KING, pieces)
        return moves

    @classmethod
    def get_positions(cls, bitboard):
        return [position for position in range(64) if (bitboard >> position) & 1]

    @classmethod
    def is_valid_position(cls, position):
        return 0 <= position <= 63

    @classmethod
    def is_occupied(cls, position, pieces):
        for piece in pieces:
            if piece and piece.is_occupied(position):
                return piece
        return None

    @classmethod
    def is_occupied_teammate(cls, position, is_white, pieces):
        for piece in pieces:
            if piece and piece.is_occupied(position) and is_white == piece.is_white():
                return piece
        return None

    @classmethod
    def is_occupied_opponent(cls, position, is_white, pieces):
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
    def remove_check_moves(cls, piece, position, moves, king, pieces, last_move, can_castle):
        piece.clear_square(position)
        for move in MovementRules.get_set_bits(moves):
            opponent = MovementRules.is_occupied_opponent(move, piece.is_white(), pieces)
            if opponent:
                opponent.clear_square(move)
            piece.occupy_square(move)
            if MovementRules.is_check(king, pieces, last_move, can_castle):
                moves &= ~(1 << move)
            piece.clear_square(move)
            if opponent:
                opponent.occupy_square(move)
        piece.occupy_square(position)
        return moves

    @classmethod
    def is_check(cls, king, pieces, last_move, can_castle):
        return any(cls.get_all_moves(bitboard, pieces, last_move, can_castle) & king.get_board()
                   for bitboard in pieces if bitboard.is_white() != king.is_white())

    @classmethod
    def is_checkmate(cls, king, pieces, last_move, can_castle):
        if not cls.is_check(king, pieces, last_move, can_castle):
            return False
        for piece in pieces:
            if piece.is_white() == king.is_white():
                positions = MovementRules.get_positions(piece.get_board())
                for position in positions:
                    moves = MovementRules.get_moves(piece, position, pieces, last_move, can_castle)
                    piece.clear_square(position)
                    for move in cls.get_set_bits(moves):
                        opponent = cls.is_occupied_opponent(move, king.is_white(), pieces)
                        if opponent:
                            opponent.clear_square(move)
                        piece.occupy_square(move)
                        if not cls.is_check(king, pieces, last_move, can_castle):
                            piece.clear_square(move)
                            piece.occupy_square(position)
                            if opponent:
                                opponent.occupy_square(move)
                            return False
                        if opponent:
                            opponent.occupy_square(move)
                        piece.clear_square(move)
                    piece.occupy_square(position)
        return True

    @classmethod
    def is_stalemate(cls, king, pieces, last_move, can_castle):
        for piece in pieces:
            if piece.is_white() == king.is_white():
                positions = MovementRules.get_positions(piece.get_board())
                for position in positions:
                    moves = cls.get_moves(piece, position, pieces, last_move, can_castle)
                    legal_moves = cls.remove_check_moves(piece, position, moves, king, pieces, last_move, can_castle)
                    if legal_moves != 0:
                        return False
        return True

    @classmethod
    def get_set_bits(cls, moves):
        # Given a binary value, return the positions of set bits (1s)
        return [i for i in range(64) if moves & (1 << i)]
