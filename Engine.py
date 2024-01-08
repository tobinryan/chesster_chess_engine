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

    def __init__(self, board):
        self.board = board

    def evaluate(self):
        if self.board.is_insufficient_material():
            return self.DRAW_VALUE
        if self.board.is_checkmate(self.board.wk):
            return -9223372036854775807
        if self.board.is_checkmate(self.board.bk):
            return 9223372036854775807

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

        value = (
                self.VALUES[Pieces.PAWN] * (len(wp) - len(bp)) +
                self.VALUES[Pieces.KNIGHT] * (len(wkn) - len(bkn)) +
                self.VALUES[Pieces.BISHOP] * (len(wb) - len(bb)) +
                self.VALUES[Pieces.ROOK] * (len(wr) - len(br)) +
                self.VALUES[Pieces.QUEEN] * (len(wq) - len(bq)) +
                sum(self.PWEIGHTS[sq] for sq in wp) - sum(self.PWEIGHTS[63 - sq] for sq in bp) +
                sum(self.KNWEIGHTS[sq] for sq in wkn) - sum(self.KNWEIGHTS[sq] for sq in bkn) +
                sum(self.BWEIGHTS[sq] for sq in wb) - sum(self.BWEIGHTS[sq] for sq in bb) +
                sum(self.RWEIGHTS[sq] for sq in wr) - sum(self.RWEIGHTS[63 - sq] for sq in br) +
                sum(self.QWEIGHTS[sq] for sq in wq) - sum(self.QWEIGHTS[63 - sq] for sq in bq) +
                sum(self.KWEIGHTS[sq] for sq in wk) - sum(self.KWEIGHTS[63 - sq] for sq in bk)

        )

        return value

    def minimax(self, depth, is_maximizing) -> Move:
        moves = []
        for piece in reversed(self.board.pieces):
            if piece.is_white() == is_maximizing:
                moves.extend(self.board.get_all_moves(piece, self.board.white_can_castle if self.board.is_white_turn
                else self.board.black_can_castle))
        best_move = -9999
        final_move = None

        for move in moves:
            self.board.make_move(move, True)
            print(self.board.last_move.end_square, self.board.last_move.start_square)
            value = max(best_move, self.alpha_beta(depth - 1, -10000, 10000, not is_maximizing))
            self.board.undo_move(move)
            if value > best_move:
                best_move = value
                final_move = move
        return final_move

    def alpha_beta(self, depth, alpha, beta, is_maximizing) -> int:
        if depth == 0:
            return self.evaluate()
        moves = []
        for piece in reversed(self.board.pieces):
            if piece.is_white() == is_maximizing:
                moves.extend(self.board.get_all_moves(piece, self.board.white_can_castle if self.board.is_white_turn
                else self.board.black_can_castle))

        bestMove = -9999 if is_maximizing else 9999
        for move in moves:
            self.board.make_move(move, True)
            if self.board.is_white_turn:
                print(self.board.last_move.start_square, self.board.last_move.end_square)
            minimax = self.alpha_beta(depth - 1, alpha, beta, not is_maximizing)
            bestMove = max(bestMove, minimax) if is_maximizing else min(bestMove, minimax)
            self.board.undo_move(move)
            if is_maximizing:
                alpha = max(alpha, bestMove)
            else:
                beta = min(beta, bestMove)
            if beta <= alpha:
                return bestMove
        return bestMove