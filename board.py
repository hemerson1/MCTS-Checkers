#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 18:38:50 2022

@author: hemerson
"""

"""
Checkers board object. 
"""

import numpy as np

from board_utils import get_moves, update_board


"""
Defines the checkers game board.
"""
class Board: 
    def __init__(self, size=8):
        
        # BOARD STRUCTURE
        self.size = size  
        self.data = np.zeros((self.size, self.size), dtype=np.int)
        number_rows_of_players = (self.size - 2)/2
        number_players_per_row = self.size/2
        
        # ensure the board size is correct
        assert self.size % 2 == 0 and self.size >= 4, "Size must be a even number >2"
        
        # construct the board
        for i in range(int(number_rows_of_players)):
            for j in range(int(number_players_per_row)):                
                if i % 2 == 0:
                    self.data[2*j, i] = -1
                    self.data[2*j + 1, self.size - (i + 1)] = +1
                else:
                    self.data[2*j + 1, i] = -1
                    self.data[2*j, self.size  - (i + 1)] = +1
                        
        # BOARD PIECES
        # black pieces, black king = 1, 2
        # white pieces, white king = -1, -2
        # empty = 0   
        self.black_symbol = 'b'
        self.black_king_symbol = 'B'
        self.white_symbol = 'w'
        self.white_king_symbol = 'W'
        self.space_symbol = ' '
    
    """
    return the possible moves for the given player.
    """
    def get_moves(self, player):        
        return get_moves(player, self.data, self.size)           
       
    """
    update the positions of the pieces.      
    """
    def update(self, player, chosen_piece, chosen_move, chosen_take):             
        self.data = update_board(player, chosen_piece, chosen_move, chosen_take, self.data, self.size)               
    
    """
    create a printed representation of the board.
    """
    def show_board(self):
        
        # convert from numbers to symbols
        symbol_data = np.char.mod('%d', self.data)        
        symbol_data = np.where(symbol_data == '1', self.black_symbol, symbol_data)        
        symbol_data = np.where(symbol_data == '2', self.black_king_symbol, symbol_data)
        symbol_data = np.where(symbol_data == '-1', self.white_symbol, symbol_data)
        symbol_data = np.where(symbol_data == '-2', self.white_king_symbol, symbol_data)
        symbol_data = np.where(symbol_data == '0', self.space_symbol, symbol_data)
        
        # print the structure of the board
        print("    " + "   ".join(map(str,[*range(self.size)])) + "  ")
        for i in range(self.size):
            print('  ---------------------------------')
            print(str(i) + " | " + " | ".join(symbol_data[i, :]) + " |")
            
        print('  ---------------------------------\n')