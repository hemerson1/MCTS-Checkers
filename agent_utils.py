#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 20:47:04 2022

@author: hemerson
"""

import random
import numpy as np

"""
Initialise the zobrist hashing function by filling a table corresponding
to the size of the board and the number of pieces with random numbers and bit strings   
"""            
def init_zobrist(size):  
    table = np.zeros((size * size, 5))

    for i in range(size * size):
        for j in range(-2, 3):

            # generate a random number
            table[i, j] = random.randint(0, 2**1000 - 1)     

    return table


"""
Create a zobrist hash for the current board set-up    
"""
def hash_board(current_board, size, hash_table):    
    h = 0        
    for i in range(size):
        for j in range(size):             
            if current_board[i, j] != 0:                
                col = current_board[i, j]                      
                h = h ^ int(hash_table[i * size + j, col])
            
    return h
