from Pieces import Pieces
from Move import Move


class Engine:
    VALUES = {Pieces.PAWN: 100, Pieces.KNIGHT: 320, Pieces.BISHOP: 330, Pieces.ROOK: 500, Pieces.QUEEN: 950}
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

    KWEIGHTS = [-30, -40, -40, -50, -50, -40, -40, -30,
                -30, -40, -40, -50, -50, -40, -40, -30,
                -30, -40, -40, -50, -50, -40, -40, -30,
                -30, -40, -40, -50, -50, -40, -40, -30,
                -20, -30, -30, -40, -40, -30, -30, -20,
                -10, -20, -20, -20, -20, -20, -20, -10,
                20, 20, 0, 0, 0, 0, 20, 20,
                20, 30, 10, 0, 0, 10, 30, 20]

    DRAW_VALUE = 0
    CHECKMATE_VALUE = 9223372036854775807

    def __init__(self, board):
        self.board = board

    def evaluate(self):
        if self.board.is_insufficient_material() or \
                self.board.is_stalemate(self.board.wk) or self.board.is_stalemate(self.board.bk):
            return self.DRAW_VALUE
        if self.board.is_checkmate(self.board.wk):
            return -self.CHECKMATE_VALUE
        if self.board.is_checkmate(self.board.bk):
            return self.CHECKMATE_VALUE

        wp = self.board.get_squares(self.board.wp.get_board())
        bp = self.board.get_squares(self.board.bp.get_board())

        wkn = self.board.get_squares(self.board.wkn.get_board())
        bkn = self.board.get_squares(self.board.bkn.get_board())

        wb = self.board.get_squares(self.board.wb.get_board())
        bb = self.board.get_squares(self.board.bb.get_board())

        wr = self.board.get_squares(self.board.wr.get_board())
        br = self.board.get_squares(self.board.br.get_board())

        wq = self.board.get_squares(self.board.wq.get_board())
        bq = self.board.get_squares(self.board.bq.get_board())

        wk = self.board.get_squares(self.board.wk.get_board())
        bk = self.board.get_squares(self.board.bk.get_board())

        eval = (
                self.VALUES[Pieces.PAWN] * (len(wp) - len(bp)) +
                self.VALUES[Pieces.KNIGHT] * (len(wkn) - len(bkn)) +
                self.VALUES[Pieces.BISHOP] * (len(wb) - len(bb)) +
                self.VALUES[Pieces.ROOK] * (len(wr) - len(br)) +
                self.VALUES[Pieces.QUEEN] * (len(wq) - len(bq)) +
                sum(self.PWEIGHTS[sq] for sq in wp) + sum(-self.PWEIGHTS[63 - sq] for sq in bp) +
                sum(self.KNWEIGHTS[sq] for sq in wkn) + sum(-self.KNWEIGHTS[sq] for sq in bkn) +
                sum(self.BWEIGHTS[sq] for sq in wb) + sum(-self.BWEIGHTS[sq] for sq in bb) +
                sum(self.RWEIGHTS[sq] for sq in wr) + sum(-self.RWEIGHTS[63 - sq] for sq in br) +
                sum(self.QWEIGHTS[sq] for sq in wq) + sum(-self.QWEIGHTS[63 - sq] for sq in bq) +
                sum(self.KWEIGHTS[sq] for sq in wk) + sum(-self.KWEIGHTS[63 - sq] for sq in bk)

        )
        if self.board.is_white_turn:
            return eval
        else:
            return -eval

    def alphabeta(self, alpha, beta, depth):
        best_score = -9999
        if depth == 0:
            return self.quiesce(alpha, beta)

        moves = self.board.get_all_moves()

        for move in moves:
            if 1 << move.end_square == self.board.wk.get_board() or 1<<move.end_square == self.board.bk.get_board():
                continue
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
        eval = self.evaluate()
        if eval >= beta:
            return beta
        if alpha < eval:
            alpha = eval

        moves = self.board.get_all_moves()

        for move in moves:
            if 1 << move.end_square == self.board.wk.get_board() or 1<<move.end_square == self.board.bk.get_board():
                continue
            if move.is_capture:
                self.board.make_move(move, True)
                score = -self.quiesce(-beta, -alpha)
                self.board.undo_move(move)
                if score >= beta:
                    return beta
                if score > alpha:
                    alpha = score
        return alpha

    def select_move(self, depth):
        best_move = None
        best_value = -99999
        alpha = -100000
        beta = 100000
        moves = self.board.get_all_moves()

        for move in moves:
            if 1 << move.end_square == self.board.wk.get_board() or 1<<move.end_square == self.board.bk.get_board():
                continue
            self.board.make_move(move, True)
            board_value = -self.alphabeta(-beta, -alpha, depth - 1)
            if board_value > best_value:
                best_value = board_value
                best_move = move
            if board_value > alpha:
                alpha = board_value
            self.board.undo_move(move)

        return best_move