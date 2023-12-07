import pygame


class BitBoard:

    def __init__(self, binary_num, icon, is_white, piece_type):
        self._board = binary_num
        self._icon = icon
        self._is_white = is_white
        self._piece_type = piece_type

    def is_occupied(self, square):
        return self._board & (1 << square)

    def clear_square(self, square):
        self._board &= ~(1 << square)

    def occupy_square(self, square):
        self._board |= (1 << square)

    def get_icon(self):
        return self._icon

    def get_board(self):
        return self._board

    def get_piece_type(self):
        return self._piece_type

    def is_white(self):
        return self._is_white

    def __str__(self):
        return bin(self._board)[2:]