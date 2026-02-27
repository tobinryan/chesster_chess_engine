import chess as chess
import chess.polyglot

from Pieces import Pieces
from Move import Move


class Engine:
    VALUES = {Pieces.PAWN: 100, Pieces.KNIGHT: 320, Pieces.BISHOP: 330, Pieces.ROOK: 500, Pieces.QUEEN: 950}

    # Phase weights for tapered eval (total starting phase = 24)
    PHASE_WEIGHTS = {Pieces.KNIGHT: 1, Pieces.BISHOP: 1, Pieces.ROOK: 2, Pieces.QUEEN: 4}
    TOTAL_PHASE = 24  # 4*1 + 4*1 + 4*2 + 2*4

    PWEIGHTS = [0, 0, 0, 0, 0, 0, 0, 0,
                50, 50, 50, 50, 50, 50, 50, 50,
                10, 10, 20, 30, 30, 20, 10, 10,
                5, 5, 10, 25, 25, 10, 5, 5,
                0, 0, 0, 20, 20, 0, 0, 0,
                5, -5, -10, 0, 0, -10, -5, 5,
                5, 10, 10, -20, -20, 10, 10, 5,
                0, 0, 0, 0, 0, 0, 0, 0]
    KNWEIGHTS = [-50, -40, -30, -30, -30, -30, -40, -50,
                 -40, -20, 0, 0, 0, 0, -20, -40,
                 -30, 0, 10, 15, 15, 10, 0, -30,
                 -30, 5, 15, 20, 20, 15, 5, -30,
                 -30, 0, 15, 20, 20, 15, 0, -30,
                 -30, 5, 10, 15, 15, 10, 5, -30,
                 -40, -20, 0, 5, 5, 0, -20, -40,
                 -50, -40, -30, -30, -30, -30, -40, -50, ]
    BWEIGHTS = [-20, -10, -10, -10, -10, -10, -10, -20,
                -10, 0, 0, 0, 0, 0, 0, -10,
                -10, 0, 5, 10, 10, 5, 0, -10,
                -10, 5, 5, 10, 10, 5, 5, -10,
                -10, 0, 10, 10, 10, 10, 0, -10,
                -10, 10, 10, 10, 10, 10, 10, -10,
                -10, 5, 0, 0, 0, 0, 5, -10,
                -20, -10, -10, -10, -10, -10, -10, -20, ]
    RWEIGHTS = [0, 0, 0, 0, 0, 0, 0, 0,
                5, 10, 10, 10, 10, 10, 10, 5,
                -5, 0, 0, 0, 0, 0, 0, -5,
                -5, 0, 0, 0, 0, 0, 0, -5,
                -5, 0, 0, 0, 0, 0, 0, -5,
                -5, 0, 0, 0, 0, 0, 0, -5,
                -5, 0, 0, 0, 0, 0, 0, -5,
                0, 0, 0, 5, 5, 0, 0, 0]

    QWEIGHTS = [-20, -10, -10, -5, -5, -10, -10, -20,
                -10, 0, 0, 0, 0, 0, 0, -10,
                -10, 0, 5, 5, 5, 5, 0, -10,
                -5, 0, 5, 5, 5, 5, 0, -5,
                0, 0, 5, 5, 5, 5, 0, -5,
                -10, 5, 5, 5, 5, 5, 0, -10,
                -10, 0, 5, 0, 0, 0, 0, -10,
                -20, -10, -10, -5, -5, -10, -10, -20]

    # Middlegame king: hide in corner, stay castled
    KWEIGHTS_MG = [-30, -40, -40, -50, -50, -40, -40, -30,
                   -30, -40, -40, -50, -50, -40, -40, -30,
                   -30, -40, -40, -50, -50, -40, -40, -30,
                   -30, -40, -40, -50, -50, -40, -40, -30,
                   -20, -30, -30, -40, -40, -30, -30, -20,
                   -10, -20, -20, -20, -20, -20, -20, -10,
                   20, 20, 0, 0, 0, 0, 20, 20,
                   20, 30, 10, 0, 0, 10, 30, 20]

    # Endgame king: centralize, be active
    KWEIGHTS_EG = [-50, -40, -30, -20, -20, -30, -40, -50,
                   -30, -20, -10, 0, 0, -10, -20, -30,
                   -30, -10, 20, 30, 30, 20, -10, -30,
                   -30, -10, 30, 40, 40, 30, -10, -30,
                   -30, -10, 30, 40, 40, 30, -10, -30,
                   -30, -10, 20, 30, 30, 20, -10, -30,
                   -30, -30, -10, 0, 0, -10, -30, -30,
                   -50, -40, -30, -20, -20, -30, -40, -50]

    # Endgame pawn: advanced pawns much more valuable
    PWEIGHTS_EG = [0, 0, 0, 0, 0, 0, 0, 0,
                   80, 80, 80, 80, 80, 80, 80, 80,
                   50, 50, 50, 50, 50, 50, 50, 50,
                   30, 30, 30, 30, 30, 30, 30, 30,
                   20, 20, 20, 20, 20, 20, 20, 20,
                   10, 10, 10, 10, 10, 10, 10, 10,
                   10, 10, 10, 10, 10, 10, 10, 10,
                   0, 0, 0, 0, 0, 0, 0, 0]

    # Pre-computed flipped PST tables for black pieces (180° rotation)
    PWEIGHTS_FLIP = PWEIGHTS[::-1]
    PWEIGHTS_EG_FLIP = PWEIGHTS_EG[::-1]
    RWEIGHTS_FLIP = RWEIGHTS[::-1]
    QWEIGHTS_FLIP = QWEIGHTS[::-1]
    KWEIGHTS_MG_FLIP = KWEIGHTS_MG[::-1]
    KWEIGHTS_EG_FLIP = KWEIGHTS_EG[::-1]

    # Passed pawn bonuses by rank (index 0 = rank 1, index 7 = rank 8)
    PASSED_PAWN_BONUS = [0, 10, 20, 40, 60, 100, 150, 0]

    # Isolated and doubled pawn penalties
    ISOLATED_PAWN_PENALTY = -15
    DOUBLED_PAWN_PENALTY = -10

    # Mop-up: center distance table for driving king to corner
    CENTER_DISTANCE = [
        6, 5, 4, 3, 3, 4, 5, 6,
        5, 4, 3, 2, 2, 3, 4, 5,
        4, 3, 2, 1, 1, 2, 3, 4,
        3, 2, 1, 0, 0, 1, 2, 3,
        3, 2, 1, 0, 0, 1, 2, 3,
        4, 3, 2, 1, 1, 2, 3, 4,
        5, 4, 3, 2, 2, 3, 4, 5,
        6, 5, 4, 3, 3, 4, 5, 6,
    ]

    # File masks for pawn structure analysis (same as Board.FILE_MASKS)
    _FILE_MASKS = [0x0101010101010101 << i for i in range(8)]

    DRAW_VALUE = 0
    CHECKMATE_VALUE = 9223372036854775807

    def __init__(self, board):
        self.board = board

    @staticmethod
    def _popcount(n):
        """Count set bits."""
        return bin(n).count('1')

    @staticmethod
    def _pst_sum(board_val, weights):
        """Sum piece-square table values for all set bits without creating intermediate lists."""
        total = 0
        while board_val:
            sq = (board_val & -board_val).bit_length() - 1
            total += weights[sq]
            board_val &= board_val - 1
        return total

    @staticmethod
    def _lsb(n):
        return (n & -n).bit_length() - 1

    @staticmethod
    def _manhattan_distance(sq1, sq2):
        r1, f1 = sq1 >> 3, sq1 & 7
        r2, f2 = sq2 >> 3, sq2 & 7
        return abs(r1 - r2) + abs(f1 - f2)

    def _game_phase(self, wkn, bkn, wb, bb, wr, br, wq, bq):
        """Calculate game phase (24 = opening, 0 = pure endgame)."""
        phase = (self._popcount(wkn) + self._popcount(bkn) +
                 self._popcount(wb) + self._popcount(bb) +
                 2 * self._popcount(wr) + 2 * self._popcount(br) +
                 4 * self._popcount(wq) + 4 * self._popcount(bq))
        return min(phase, self.TOTAL_PHASE)

    def _passed_pawns_score(self, wp, bp):
        """Evaluate passed pawns for both sides."""
        score = 0
        # White passed pawns: no black pawn on same file or adjacent files ahead
        pawns = wp
        while pawns:
            sq = self._lsb(pawns)
            file = sq & 7
            rank = sq >> 3
            # Create a mask of all squares ahead on same + adjacent files
            blocked = False
            for f in range(max(0, file - 1), min(8, file + 2)):
                # Check all ranks above this pawn for black pawns
                check_mask = self._FILE_MASKS[f]
                # Mask ranks above: shift to clear ranks at or below current rank
                above_mask = check_mask & ~((1 << ((rank + 1) * 8)) - 1)
                if bp & above_mask:
                    blocked = True
                    break
            if not blocked:
                score += self.PASSED_PAWN_BONUS[rank]
            pawns &= pawns - 1

        # Black passed pawns
        pawns = bp
        while pawns:
            sq = self._lsb(pawns)
            file = sq & 7
            rank = sq >> 3
            blocked = False
            for f in range(max(0, file - 1), min(8, file + 2)):
                check_mask = self._FILE_MASKS[f]
                # Mask ranks below: only ranks below current rank
                below_mask = check_mask & ((1 << (rank * 8)) - 1)
                if wp & below_mask:
                    blocked = True
                    break
            if not blocked:
                score -= self.PASSED_PAWN_BONUS[7 - rank]
            pawns &= pawns - 1

        return score

    def _pawn_structure_score(self, wp, bp):
        """Evaluate pawn structure: isolated and doubled pawns."""
        score = 0
        for f in range(8):
            w_on_file = self._popcount(wp & self._FILE_MASKS[f])
            b_on_file = self._popcount(bp & self._FILE_MASKS[f])

            # Doubled pawns
            if w_on_file > 1:
                score += self.DOUBLED_PAWN_PENALTY * (w_on_file - 1)
            if b_on_file > 1:
                score -= self.DOUBLED_PAWN_PENALTY * (b_on_file - 1)

            # Isolated pawns (no friendly pawn on adjacent files)
            adj_mask = 0
            if f > 0:
                adj_mask |= self._FILE_MASKS[f - 1]
            if f < 7:
                adj_mask |= self._FILE_MASKS[f + 1]

            if w_on_file > 0 and not (wp & adj_mask):
                score += self.ISOLATED_PAWN_PENALTY * w_on_file
            if b_on_file > 0 and not (bp & adj_mask):
                score -= self.ISOLATED_PAWN_PENALTY * b_on_file

        return score

    def _mopup_score(self, wk, bk, material_score):
        """
        Mop-up evaluation: when one side has a large material advantage,
        encourage driving the losing king to the corner and bringing
        the winning king close.
        """
        if abs(material_score) < 200:
            return 0

        wk_sq = self._lsb(wk)
        bk_sq = self._lsb(bk)

        king_dist = self._manhattan_distance(wk_sq, bk_sq)

        if material_score > 0:
            # White is winning: push black king to corner, bring white king close
            return (self.CENTER_DISTANCE[bk_sq] * 10 +
                    (14 - king_dist) * 4)
        else:
            # Black is winning: push white king to corner, bring black king close
            return -(self.CENTER_DISTANCE[wk_sq] * 10 +
                     (14 - king_dist) * 4)

    def evaluate(self):
        # Get all bitboards
        wp = self.board.wp.get_board()
        bp = self.board.bp.get_board()
        wkn = self.board.wkn.get_board()
        bkn = self.board.bkn.get_board()
        wb = self.board.wb.get_board()
        bb = self.board.bb.get_board()
        wr = self.board.wr.get_board()
        br = self.board.br.get_board()
        wq = self.board.wq.get_board()
        bq = self.board.bq.get_board()
        wk = self.board.wk.get_board()
        bk = self.board.bk.get_board()

        pst = self._pst_sum
        popcount = self._popcount

        # ---- Game phase (tapered eval) ----
        phase = self._game_phase(wkn, bkn, wb, bb, wr, br, wq, bq)
        eg_weight = self.TOTAL_PHASE - phase  # 0 in opening, 24 in pure endgame

        # ---- Material ----
        material = (
                100 * (popcount(wp) - popcount(bp)) +
                320 * (popcount(wkn) - popcount(bkn)) +
                330 * (popcount(wb) - popcount(bb)) +
                500 * (popcount(wr) - popcount(br)) +
                950 * (popcount(wq) - popcount(bq))
        )

        # ---- Piece-square tables (non-king, non-pawn are phase-independent) ----
        positional = (
                pst(wkn, self.KNWEIGHTS) - pst(bkn, self.KNWEIGHTS) +
                pst(wb, self.BWEIGHTS) - pst(bb, self.BWEIGHTS) +
                pst(wr, self.RWEIGHTS) - pst(br, self.RWEIGHTS_FLIP) +
                pst(wq, self.QWEIGHTS) - pst(bq, self.QWEIGHTS_FLIP)
        )

        # ---- Tapered pawn PST ----
        pawn_mg = pst(wp, self.PWEIGHTS) - pst(bp, self.PWEIGHTS_FLIP)
        pawn_eg = pst(wp, self.PWEIGHTS_EG) - pst(bp, self.PWEIGHTS_EG_FLIP)
        pawn_score = (pawn_mg * phase + pawn_eg * eg_weight) // self.TOTAL_PHASE

        # ---- Tapered king PST ----
        king_mg = pst(wk, self.KWEIGHTS_MG) - pst(bk, self.KWEIGHTS_MG_FLIP)
        king_eg = pst(wk, self.KWEIGHTS_EG) - pst(bk, self.KWEIGHTS_EG_FLIP)
        king_score = (king_mg * phase + king_eg * eg_weight) // self.TOTAL_PHASE

        # ---- Pawn structure ----
        structure = self._pawn_structure_score(wp, bp)

        # ---- Passed pawns (scaled by endgame weight) ----
        passed = self._passed_pawns_score(wp, bp)
        # Passed pawn bonus matters more in endgame
        passed = (passed * (phase + eg_weight * 2)) // (self.TOTAL_PHASE * 2)

        # ---- Mop-up evaluation ----
        mopup = self._mopup_score(wk, bk, material)

        score = material + positional + pawn_score + king_score + structure + passed + mopup

        return score if self.board.is_white_turn else -score

    def alphabeta(self, alpha, beta, depth):
        if depth == 0:
            return self.quiesce(alpha, beta)

        king = self.board.wk if self.board.is_white_turn else self.board.bk
        moves = self.board.get_all_moves()
        moves = self.board.remove_check_moves(moves, king)

        # No legal moves: checkmate or stalemate
        if not moves:
            if self.board.is_check(king):
                return -self.CHECKMATE_VALUE
            return self.DRAW_VALUE

        moves.sort(key=Move.move_sort_key)
        best_score = -float('inf')

        for move in moves:
            self.board.make_move(move, True)
            score = -self.alphabeta(-beta, -alpha, depth - 1)
            self.board.undo_move(move)
            if score >= beta:
                return score
            if score > best_score:
                best_score = score
            if score > alpha:
                alpha = score
        return best_score

    def quiesce(self, alpha, beta):
        stand_pat = self.evaluate()
        if stand_pat >= beta:
            return beta
        if stand_pat > alpha:
            alpha = stand_pat

        king = self.board.wk if self.board.is_white_turn else self.board.bk
        moves = self.board.get_all_moves()
        # Filter captures before legality check to reduce remove_check_moves work
        captures = [m for m in moves if m.is_capture]
        captures = self.board.remove_check_moves(captures, king)
        captures.sort(key=Move.move_sort_key)

        for move in captures:
            self.board.make_move(move, True)
            score = -self.quiesce(-beta, -alpha)
            self.board.undo_move(move)
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
        return alpha

    def select_move(self, depth):
        try:
            fen = self.board.export_fen()
            if self.board.engine_side:
                fen = self.board.flip_fen(fen)
            board_rep = chess.Board(fen)
            polyglot_move = chess.polyglot.MemoryMappedReader("Titans.bin").weighted_choice(board_rep).move
            return self.polyglot_to_move(polyglot_move)
        except:
            best_move = None
            best_value = -99999
            alpha = -100000
            beta = 100000
            king = self.board.wk if self.board.is_white_turn else self.board.bk
            moves = self.board.get_all_moves()
            moves = self.board.remove_check_moves(moves, king)
            moves.sort(key=Move.move_sort_key)

            for move in moves:
                self.board.make_move(move, True)
                board_value = -self.alphabeta(-beta, -alpha, depth - 1)
                if board_value > best_value:
                    best_value = board_value
                    best_move = move
                if board_value > alpha:
                    alpha = board_value
                self.board.undo_move(move)

            return best_move

    def polyglot_to_move(self, polyglot) -> Move:
        piece = self.board.get_piece(polyglot.from_square)
        move = Move(polyglot.from_square, polyglot.to_square, piece.get_piece_type(),
                    self.board.get_occupied() & 1 << polyglot.to_square)
        if self.board.engine_side:
            move.flip()
        return move
