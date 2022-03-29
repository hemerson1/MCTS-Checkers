#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 18:41:45 2022

@author: hemerson
"""

import numpy as np

"""
Return all the possible moves for a given player based 
on the board configuration.
"""
def get_moves(player, data, size):
    possible_moves = dict()
    possible_pieces_taken = dict()

    # initialise the pieces 
    w_piece_locations = np.argwhere(data == -1)
    w_king_locations = np.argwhere(data == -2)
    b_piece_locations = np.argwhere(data == 1)
    b_king_locations = np.argwhere(data == 2)
    empty_spaces = np.argwhere(data == 0)
    player_piece_locations = None
    player_king_locations = None
    enemy_piece_locations = None
    forward = None        

    # Check the player colour  
    if player == 'white':
        player_piece_locations = w_piece_locations
        player_king_locations = w_king_locations
        enemy_piece_locations = np.concatenate([b_piece_locations, b_king_locations])  
        forward = +1
    elif player == 'black':
        player_piece_locations = b_piece_locations
        player_king_locations = b_king_locations
        enemy_piece_locations = np.concatenate([w_piece_locations, w_king_locations])   
        forward = -1 

    # for regular pieces --------------------------
    for coord in player_piece_locations:

        moves = np.empty((0, 2), dtype=np.int)

        # set starting coordinates                
        row, col = coord[0], coord[1]

        # calculate simple moves --------------------------

        # move down
        if row + 1 != size:
            move = np.array([[row + 1, col + forward]])

            if np.any((empty_spaces == move[0]).all(axis=1)):
                moves = np.append(moves, move, axis=0)

        # move up
        if row - 1 != -1:
            move = np.array([[row - 1, col + forward]])

            if np.any((empty_spaces == move[0]).all(axis=1)):
                moves = np.append(moves, move, axis=0)

        # calculate jump moves --------------------------

        jumps = [np.expand_dims(coord, axis=0)]
        pieces_taken = list()

        prev_jump = 0
        current_jump = 1

        taken_count = 0

        while True:

            # number of new jumps in last cycle                    
            new_jumps =  current_jump - prev_jump

            # number of total jumps excluding those added last cycle
            prev_jump_copy = prev_jump  

            # update the counts
            prev_jump = current_jump
            taken_count_copy = taken_count

            for j in range(new_jumps):

                # get the new jump coordinate from the last cycle
                new_jump_coord = jumps[prev_jump_copy + j]

                row, col = new_jump_coord[-1, 0], new_jump_coord[-1, 1]

                # jump down
                if row + 2 <= size:
                    move = np.array([[row + 2, col + (2 * forward)]])
                    jump_piece = np.array([[row + 1, col + forward]])

                    # if the move is onto an empty space and the jump is over an enemy piece
                    if np.any((empty_spaces == move[0]).all(axis=1)) and np.any((enemy_piece_locations == jump_piece[0]).all(axis=1)):                                  

                        # add new jump to path
                        jump_path = np.append(new_jump_coord, move,  axis=0)
                        jumps.append(jump_path)      

                        # if there is already a jump in the path append to it
                        if taken_count_copy > 0:                                    
                            jump_piece = np.append(pieces_taken[prev_jump_copy + j - 1], jump_piece, axis=0)

                        # update the taken pieces and jumps
                        pieces_taken.append(jump_piece)
                        current_jump += 1
                        taken_count += 1

                # jump up
                if row - 2 >= 0:
                    move = np.array([[row - 2, col + (2 * forward)]])
                    jump_piece = np.array([[row - 1, col + forward]])

                    # if the move is onto an empty space and the jump is over an enemy piece
                    if np.any((empty_spaces == move[0]).all(axis=1)) and np.any((enemy_piece_locations == jump_piece[0]).all(axis=1)):                                  

                        # add new jump to path
                        jump_path = np.append(new_jump_coord, move,  axis=0)
                        jumps.append(jump_path)      

                        # if there is already a jump in the path append to it
                        if taken_count_copy > 0:                                    
                            jump_piece = np.append(pieces_taken[prev_jump_copy + j - 1], jump_piece, axis=0)

                        # update the taken pieces and jumps
                        pieces_taken.append(jump_piece)
                        current_jump += 1
                        taken_count += 1                              

            if current_jump == prev_jump:
                break

        # return the moves for all normal pieces

        # if there were any jump moves
        if len(jumps) > 1:

            cleaned_jumps = list()
            cleaned_takes = list()

            for i in range(1, len(jumps)):  

                intermediate = False

                # check if this is an intermediate step
                for j in range(i + 1, len(jumps)):                             
                    if np.array_equal(jumps[i], jumps[j][:-1, :]): 
                        intermediate = True

                # if its not an intermediate step add it to the clean jumps
                if not intermediate:                             
                    cleaned_jump = jumps[i][-1, :]
                    cleaned_jumps.append(cleaned_jump)

                    cleaned_take = pieces_taken[i - 1]
                    cleaned_takes.append(cleaned_take)

            possible_moves[(coord[0], coord[1])] = np.array(cleaned_jumps)
            possible_pieces_taken[(coord[0], coord[1])] = cleaned_takes

        else:
            # if there were any normal moves
            if moves.shape[0] > 0:                    
                possible_moves[(coord[0], coord[1])] = moves


    # for king pieces --------------------------
    for coord in player_king_locations:

        moves = np.empty((0, 2), dtype=np.int)

        # set starting coordinates   
        row, col = coord[0], coord[1]

        # calculate simple moves --------------------------

        # move down + forward
        if row + 1 != size:
            move = np.array([[row + 1, col + forward]])

            if np.any((empty_spaces == move[0]).all(axis=1)):
                moves = np.append(moves, move, axis=0)

        # move up + forward
        if row - 1 != -1:
            move = np.array([[row - 1, col + forward]])

            if np.any((empty_spaces == move[0]).all(axis=1)):                
                moves = np.append(moves, move, axis=0)                        

        # move down + backward
        if col + forward != size:
            move = np.array([[row + 1, col - forward]])

            if np.any((empty_spaces == move[0]).all(axis=1)):                
                moves = np.append(moves, move, axis=0)

        # move up + backward
        if col - forward != -1:
            move = np.array([[row - 1, col - forward]])

            if np.any((empty_spaces == move[0]).all(axis=1)):
                moves = np.append(moves, move, axis=0)

        # calculate jump moves --------------------------

        jumps = [np.expand_dims(coord, axis=0)]
        pieces_taken = list()

        prev_jump = 0
        current_jump = 1                
        taken_count = 0

        while True:

            # number of new jumps in last cycle                    
            new_jumps =  current_jump - prev_jump

            # number of total jumps excluding those added last cycle
            prev_jump_copy = prev_jump  

            # update the counts
            prev_jump = current_jump                    
            taken_count_copy = taken_count

            for j in range(new_jumps):                          

                # get the new jump coordinate from the last cycle
                new_jump_coord = jumps[prev_jump_copy + j]                        
                row, col = new_jump_coord[-1, 0], new_jump_coord[-1, 1]

                # jump down + forward
                if row + 2 <= size:
                    move = np.array([[row + 2, col + (2 * forward)]])
                    jump_piece = np.array([[row + 1, col + forward]])

                    # if the move is onto an empty space and the jump is over an enemy piece
                    if (np.any((empty_spaces == move[0]).all(axis=1)) or np.array_equal(coord, move[0])) and np.any((enemy_piece_locations == jump_piece[0]).all(axis=1)):        

                        # check if this jump is over the piece previously jumped
                        condition = False
                        if taken_count_copy > 0:
                            condition = np.any((pieces_taken[prev_jump_copy + j - 1] == jump_piece[0]).all(axis=1))

                        if not condition:

                            # add new jump to path
                            jump_path = np.append(new_jump_coord, move,  axis=0)
                            jumps.append(jump_path)      

                            # if there is already a jump in the path append to it  
                            if taken_count_copy > 0:                                     
                                jump_piece = np.append(pieces_taken[prev_jump_copy + j - 1], jump_piece, axis=0)

                            # update the taken pieces and jumps
                            pieces_taken.append(jump_piece)
                            current_jump += 1
                            taken_count += 1

                # jump up + forward
                if row - 2 >= 0:
                    move = np.array([[row - 2, col + (2 * forward)]])
                    jump_piece = np.array([[row - 1, col + forward]])

                    # if the move is onto an empty space and the jump is over an enemy piece
                    if (np.any((empty_spaces == move[0]).all(axis=1)) or np.array_equal(coord, move[0])) and np.any((enemy_piece_locations == jump_piece[0]).all(axis=1)):        

                        # check if this jump is over the piece previously jumped
                        condition = False
                        if taken_count_copy > 0:
                            condition = np.any((pieces_taken[prev_jump_copy + j - 1] == jump_piece[0]).all(axis=1))

                        if not condition:

                            # add new jump to path
                            jump_path = np.append(new_jump_coord, move,  axis=0)
                            jumps.append(jump_path)      

                            # if there is already a jump in the path append to it  
                            if taken_count_copy > 0:                                     
                                jump_piece = np.append(pieces_taken[prev_jump_copy + j - 1], jump_piece, axis=0)

                            # update the taken pieces and jumps
                            pieces_taken.append(jump_piece)
                            current_jump += 1
                            taken_count += 1                         

                # jump down + backward
                if row + 2 <= size:
                    move = np.array([[row + 2, col - (2 * forward)]])
                    jump_piece = np.array([[row + 1, col - forward]])

                    # if the move is onto an empty space and the jump is over an enemy piece
                    if (np.any((empty_spaces == move[0]).all(axis=1)) or np.array_equal(coord, move[0])) and np.any((enemy_piece_locations == jump_piece[0]).all(axis=1)):        

                        # check if this jump is over the piece previously jumped
                        condition = False
                        if taken_count_copy > 0:
                            condition = np.any((pieces_taken[prev_jump_copy + j - 1] == jump_piece[0]).all(axis=1))

                        if not condition:

                            # add new jump to path
                            jump_path = np.append(new_jump_coord, move,  axis=0)
                            jumps.append(jump_path)      

                            # if there is already a jump in the path append to it  
                            if taken_count_copy > 0:                                     
                                jump_piece = np.append(pieces_taken[prev_jump_copy + j - 1], jump_piece, axis=0)

                            # update the taken pieces and jumps
                            pieces_taken.append(jump_piece)
                            current_jump += 1
                            taken_count += 1

                # jump up + backward
                if row - 2 >= 0:
                    move = np.array([[row - 2, col - (2 * forward)]])
                    jump_piece = np.array([[row - 1, col - forward]])

                    # if the move is onto an empty space and the jump is over an enemy piece
                    if (np.any((empty_spaces == move[0]).all(axis=1)) or np.array_equal(coord, move[0])) and np.any((enemy_piece_locations == jump_piece[0]).all(axis=1)):        

                        # check if this jump is over the piece previously jumped
                        condition = False
                        if taken_count_copy > 0:
                            condition = np.any((pieces_taken[prev_jump_copy + j - 1] == jump_piece[0]).all(axis=1))

                        if not condition:

                            # add new jump to path
                            jump_path = np.append(new_jump_coord, move,  axis=0)
                            jumps.append(jump_path)      

                            # if there is already a jump in the path append to it  
                            if taken_count_copy > 0:                                     
                                jump_piece = np.append(pieces_taken[prev_jump_copy + j - 1], jump_piece, axis=0)

                            # update the taken pieces and jumps
                            pieces_taken.append(jump_piece)
                            current_jump += 1
                            taken_count += 1                             

            # if no new jumps were added
            if current_jump == prev_jump:
                break

         # return the moves for all normal pieces              

        # if there were any jump moves
        if len(jumps) > 1:

            cleaned_jumps = list()
            cleaned_takes = list()

            for i in range(1, len(jumps)):  

                intermediate = False

                # check if this is an intermediate step
                for j in range(i + 1, len(jumps)):                             
                    if np.array_equal(jumps[i], jumps[j][:-1, :]): 
                        intermediate = True

                if not intermediate:                             
                    cleaned_jump = jumps[i][-1, :]
                    cleaned_jumps.append(cleaned_jump)

                    cleaned_take = pieces_taken[i - 1]
                    cleaned_takes.append(cleaned_take)

            possible_moves[(coord[0], coord[1])] = np.array(cleaned_jumps)
            possible_pieces_taken[(coord[0], coord[1])] = cleaned_takes

        else:
            # if there were any normal moves
            if moves.shape[0] > 0:                    
                possible_moves[(coord[0], coord[1])] = moves

    return possible_moves, possible_pieces_taken  


"""
Given the current grid positiion update the board with a specified
move and remove all the taken pieces. 
"""
def update_board(player, chosen_piece, chosen_move, chosen_take, data, size):

    king_piece_type = None
    king_col = None

    # idenitfy player type
    if player == 'white':
        king_piece_type = -2
        king_col = size - 1
    elif player == 'black':
        king_piece_type = 2
        king_col = 0

    piece_type = data[chosen_piece[0], chosen_piece[1]]

    # now king?
    if chosen_move[1] == king_col:
        piece_type = king_piece_type

    # set previous location to empty and add new piece according to move
    data[chosen_piece[0], chosen_piece[1]] = 0
    data[chosen_move[0], chosen_move[1]] = piece_type

    # cycle through and remove the taken pieces
    if len(chosen_take) > 0:         
        for i in range(chosen_take.shape[0]):                    
            data[chosen_take[i, 0], chosen_take[i, 1]] = 0    
            
    return data    