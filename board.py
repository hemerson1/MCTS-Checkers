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
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

from board_utils import get_moves, update_board


"""
Defines the checkers game board.
"""
class Board: 
    def __init__(self, size=8):
        
        # BOARD STRUCTURE
        self.size = size  
        self.data = np.zeros((self.size, self.size), dtype=int)
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
        
        # display settings
        self.first_call = True
        self.fps = 1
        self.white = (255, 255, 255)
        self.black = (0, 0, 0) 
        self.gray = (108, 103, 105)
        self.light_wood = (191,169,112)
        self.dark_wood = (64,39,23)
        self.red = (199, 25, 45)
        
        
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
    def show_board(self, visual):
        
        # initialise the pygame environment
        if self.first_call and (visual == "pygame" or visual == "video"):
            
            # restart the pygame window
            pygame.display.quit()
            pygame.init()                  
            pygame.display.set_caption("Checkers MCTS")  
            
            # set the font, clock, etc.            
            self.font = pygame.font.Font(None, 24)
            self.clock = pygame.time.Clock()
            self.window_width, self.window_height = 414, 414
            self.screen = pygame.display.set_mode([self.window_width, self.window_height])
            self.first_call = False
            
            # configure the video
            self.image_count = 0 
            current_dir = os.path.abspath(os.getcwd())
            self.image_folder = current_dir + "/images"
            if not os.path.exists(self.image_folder):
                os.makedirs(self.image_folder)            
        
        # convert from numbers to symbols
        symbol_data = np.char.mod('%d', self.data)        
        symbol_data = np.where(symbol_data == '1', self.black_symbol, symbol_data)        
        symbol_data = np.where(symbol_data == '2', self.black_king_symbol, symbol_data)
        symbol_data = np.where(symbol_data == '-1', self.white_symbol, symbol_data)
        symbol_data = np.where(symbol_data == '-2', self.white_king_symbol, symbol_data)
        symbol_data = np.where(symbol_data == '0', self.space_symbol, symbol_data)
        
        if visual == "terminal":
        
            # print the structure of the board
            print("    " + "   ".join(map(str,[*range(self.size)])) + "  ")
            for i in range(self.size):
                print('  ---------------------------------')
                print(str(i) + " | " + " | ".join(symbol_data[i, :]) + " |")
                
            print('  ---------------------------------\n')
            
            
        if visual == "pygame" or visual == "video":  
            
            # quit the game
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    pygame.display.quit()
                            
            # set the background colour to green
            self.screen.fill(self.white)
            
            # set the size of the block
            block_size = int(self.window_height/(self.size + 1))
            
            for x in range(0, self.window_width, block_size):
                for y in range(0, self.window_height, block_size):
                    
                    text = ""
                    colour = self.white
                    text_colour = self.black
                    
                    grid_x, grid_y = int(x/block_size), int(y/block_size)                                         
                    if grid_x < self.size and grid_y < self.size: 
                        
                        # colour the grid
                        if abs(grid_x - grid_y) % 2 == 0:                        
                            colour = self.white    
                            
                        if abs(grid_x - grid_y) % 2 == 1:                        
                            colour = self.black
                        
                        if symbol_data[grid_x, grid_y] == self.black_symbol:
                            text, text_colour = "o", self.red
                            
                        if symbol_data[grid_x, grid_y] == self.white_symbol:
                            text, text_colour  = "o", self.gray
                            
                        if symbol_data[grid_x, grid_y] == self.black_king_symbol:
                            text, text_colour = "O", self.red      
                            
                        if symbol_data[grid_x, grid_y] == self.white_king_symbol:
                            text, text_colour = "O", self.gray
                            
                    if grid_x == self.size and grid_y != self.size:
                        text = str(grid_y)
                        
                    if grid_y == self.size and grid_x != self.size:
                        text = str(grid_x)
                    
                    # create the rect for the grid
                    rect = pygame.Rect(x, y, block_size, block_size)
                    
                    # get the centred text                    
                    text_surface = self.font.render(text, True, text_colour)
                    text_rect = text_surface.get_rect(center=(rect.x + block_size/2, rect.y + block_size/2))  
                    
                    # draw the square
                    pygame.draw.rect(self.screen, colour, rect)   
                    self.screen.blit(text_surface, text_rect)
                    
            # to save as video
            if visual == "video":
                pygame.image.save(self.screen, self.image_folder + "/" + str(self.image_count).rjust(4, '0') + "_screenshot.png")
                self.image_count += 1
                    
            # update the display
            pygame.display.update()
            
            # update the frame rate
            self.clock.tick(self.fps)
            
        
if __name__ == "__main__":
    
    
    board = Board()
    board.show_board(visual="pygame")
    
    
    