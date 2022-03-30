#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 18:39:20 2022

@author: hemerson
"""

import random, math, pickle
import numpy as np

from board_utils import get_moves, update_board
from agent_utils import hash_board, init_zobrist

"""
Defines a template class for the agent.
"""
class Actor: 
    def __init__(self,  player):
        self.player = player
    
    """
    Ensure that jump moves are taken with priority in accordance
    with the rules of english draughts
    """
    def ensure_jump(self, possible_moves, pieces_taken):
        
        corrected_moves = dict()        
        if len(pieces_taken) > 0:            
            for coords in pieces_taken:                
                corrected_moves[coords] = possible_moves[coords]            
            return corrected_moves
        
        else:
            return possible_moves
    
    """
    Select the action from the possible moves available
    """        
    def select_action(self, possible_moves, pieces_taken):
        # Not implemented
        pass
        

"""
Defines an actor which selects moves at random in
accordance with the rules of english draughts
"""
class Random_Actor(Actor): 
    def __init__(self,  player):
        super().__init__(player)
    
    """
    Consider the available moves and returns the piece location (tuple),
    move location (list) and coords of pieces taken (list of np arrays).     
    """    
    def select_action(self, possible_moves, pieces_taken, current_board):        
        
        # ensure jump moves are prioritised if possible
        corrected_moves = self.ensure_jump(possible_moves, pieces_taken)  
        
        # randomly select a piece from possible pieces
        starting_point, moves = random.choice(list(corrected_moves.items()))
        
        # randomly select a move for that piece
        chosen_index = np.random.choice(moves.shape[0], size=1, replace=False)        
        chosen_move = moves[chosen_index, :]
        
        # get the taken pieces
        chosen_pieces = []
        if len(pieces_taken) > 0:
            chosen_pieces = pieces_taken[starting_point][chosen_index[0]]
            
        return starting_point, chosen_move[-1, :], chosen_pieces  
    

"""
Defines the Monte Carlo Tree Search Agent
"""
class MCTS_Actor(Actor): 
    def __init__(self,  player, size):
        super().__init__(player)
        
        # specifiy the learning parameters
        self.number_sims = 100
        self.UCB = 1.5
        self.size = size
        
        # get the enemy colour
        if self.player == 'white': self.enemy_player = 'black'
        else: self.enemy_player = 'white'            
        
        # STATISTICS 
        self.values = dict()
        self.plays = dict()
        self.history = []
        
        # HASHING
        self.size = size
        self.hash_table = init_zobrist(self.size)
        
    """
    Consider the available moves and selects the opitmal move
    returning the piece location (tuple), move location (list) 
    and coords of pieces taken (list of np arrays).     
    """      
    def select_action(self, input_possible_moves, input_pieces_taken, input_board):     
        
        # ensure jump moves are prioritised if possible
        input_corrected_moves = self.ensure_jump(input_possible_moves, input_pieces_taken) 
        input_hash = hash_board(input_board, self.size, self.hash_table)
        
        # add the original state
        if input_hash not in self.values:            
            self.plays[input_hash] = 0
            self.values[input_hash] = 0   
            
        for i in range(self.number_sims):   
            
            # clear the history 
            self.history.clear()
            current_board = input_board.copy()
            self.history.append(input_hash)
            
            # reset the state
            corrected_moves = input_corrected_moves
            pieces_taken = input_pieces_taken
            player = self.player
            
            stalemate = False
            move_count = 0
            max_move_count = 200
            
            # SELECTION: -----------------------------------------------------------------------
            # picks a successor by applying the UCB strategy
            # as long as statistics exist for all successors
            
            previously_visited, new_moves, new_pieces_taken = self.new_playable_states(corrected_moves, pieces_taken, current_board, player)
            playable_moves = bool(corrected_moves)
            
            # while all the possible moves have already been made and the game is not over 
            while previously_visited and playable_moves and not stalemate: 
            
                # choose an action using UCB and update the board
                chosen_piece, chosen_move, chosen_take = self.selection(corrected_moves, pieces_taken, current_board, player)                  
                new_board = update_board(player, chosen_piece, chosen_move, chosen_take, current_board, self.size) 
                new_board_hash = hash_board(new_board, self.size, self.hash_table)
                self.history.append(new_board_hash)     
                
                # update the current player
                if player == self.player: player = self.enemy_player
                else: player = self.player
                
                # update the moves for the new board
                possible_moves, pieces_taken = get_moves(player, new_board, self.size)
                corrected_moves = self.ensure_jump(possible_moves, pieces_taken) 
                current_board = new_board
                
                # update the loop condition
                previously_visited, new_moves, new_pieces_taken = self.new_playable_states(corrected_moves, pieces_taken, current_board, player)
                playable_moves = bool(corrected_moves)
                stalemate = np.count_nonzero(current_board) < 3
                
                move_count += 1                
                if move_count > max_move_count: stalemate = True
            
            # EXPANSION: -----------------------------------------------------------------------------
            # picks a random successor (with no statistics) and adds it to the statistics
            
            if playable_moves and not stalemate: 
                
                # randomly select a piece from possible pieces
                chosen_piece, moves = random.choice(list(new_moves.items()))

                # randomly select a move for that piece
                chosen_index = np.random.choice(moves.shape[0], size=1, replace=False)
                chosen_move = moves[chosen_index, :][-1, :]
                
                # get the taken pieces
                chosen_take = []
                if len(new_pieces_taken) > 0:                    
                    chosen_take = new_pieces_taken[chosen_piece][chosen_index[0]]
                    
                new_board = update_board(player, chosen_piece, chosen_move, chosen_take, current_board, self.size) 
                new_board_hash = hash_board(new_board, self.size, self.hash_table)
                
                # update statistics
                self.history.append(new_board_hash)
                self.plays[new_board_hash] = 0
                self.values[new_board_hash] = 0
                    
                # update the current player
                if player == self.player: player = self.enemy_player
                else: player = self.player       
                
                # update the moves for the new board
                possible_moves, new_pieces_taken = get_moves(player, new_board, self.size)
                new_moves = self.ensure_jump(possible_moves, new_pieces_taken) 
                current_board = new_board
                
                # update the loop condition
                playable_moves = bool(new_moves)
                stalemate = np.count_nonzero(new_board) < 3
                
                move_count += 1                
                if move_count > max_move_count: stalemate = True
            
            # (LIGHT) PLAYOUT: ---------------------------------------------------------------
            # picks random successors until the end of the play
            
            while playable_moves and not stalemate:
                                
                # randomly select a piece from possible pieces
                chosen_piece, moves = random.choice(list(new_moves.items()))

                # randomly select a move for that piece
                chosen_index = np.random.choice(moves.shape[0], size=1, replace=False)
                chosen_move = moves[chosen_index, :][-1, :]
                
                # get the taken pieces
                chosen_take = []
                if len(new_pieces_taken) > 0:
                    chosen_take = new_pieces_taken[chosen_piece][chosen_index[0]]                                                                      
                    
                new_board = update_board(player, chosen_piece, chosen_move, chosen_take, current_board, self.size) 
                
                # update the current player
                if player == self.player: player = self.enemy_player
                else: player = self.player      
                    
                # update the moves for the new board
                possible_moves, new_pieces_taken = get_moves(player, new_board, self.size)
                new_moves = self.ensure_jump(possible_moves, new_pieces_taken) 
                current_board = new_board
                
                # update the loop condition
                playable_moves = bool(new_moves)
                stalemate = np.count_nonzero(new_board) < 3
                
                move_count += 1                
                if move_count > max_move_count: stalemate = True
            
            # BACKPROPAGATION: ------------------------------------------------------------
            # updates the statistics of states in history   
            
            # black loses
            if player == 'black': 
                outcome = 1
                
            # white loses
            elif player == 'white': 
                outcome = -1
                
            if stalemate: 
                outcome = 0
            
            self.backpropagate(outcome) 
            
        # Choose the action to maximise/minimise the value
        
        # get the action hashes
        action_hash_val = list()
            
        # get the starting location and action corresponding to the hash
        actions_to_take = list()
        
        # cycle through positions with available moves
        for key, value in input_corrected_moves.items():
            
            # cycle through the possible moves at that position
            for i in range(value.shape[0]):
                
                # create a copy of the array to avoid editing the original
                current_board_copy = input_board.copy()
                
                chosen_piece = key
                chosen_move = value[i, :]
                chosen_take = []
                
                if key in input_pieces_taken:
                    chosen_take = input_pieces_taken[key][i] 
                
                # get the new state and hash it
                new_board = update_board(self.player, chosen_piece, chosen_move, chosen_take, current_board_copy, self.size)   
                new_hash = hash_board(new_board, self.size, self.hash_table) 
                action_hash_val.append(self.values[new_hash])                       
                                                
                # save the original position of the piece taking the action 
                # and the row of the action
                actions_to_take.append([chosen_piece, chosen_move, chosen_take])   
        
        if self.player == 'white':            
            max_vals = np.argwhere(action_hash_val == np.amax(action_hash_val))            
            action = np.random.choice(max_vals.flatten(), 1, replace=False)[0]            
            
        elif self.player == 'black':
            max_vals = np.argwhere(action_hash_val == np.amin(action_hash_val))            
            action = np.random.choice(max_vals.flatten(), 1, replace=False)[0]     
        
        # return the chosen_piece, chosen_move, chosen_take
        return actions_to_take[action][0], actions_to_take[action][1], actions_to_take[action][2]
    
    
    """
    Select an action using the upper confidence 
    bound strategy (UCB)
    """
    def selection(self, possible_actions, pieces_taken, current_board, player):
        
        # get hash for the current board config        
        current_hash = hash_board(current_board, self.size, self.hash_table)  
        
        # get the action hashes
        action_hash = list()
        
        # get the starting location and action corresponding to the hash
        actions_to_take = list()
        
        # cycle through positions with available moves
        for key, value in possible_actions.items():
            
            # cycle through the possible moves at that position
            for i in range(value.shape[0]):
                
                # create a copy of the array to avoid editing the original
                current_board_copy = current_board.copy()
                
                chosen_piece = key
                chosen_move = value[i, :]
                chosen_take = []
                
                if key in pieces_taken:
                    chosen_take = pieces_taken[key][i] 
                
                # get the new state and hash it
                new_board = update_board(player, chosen_piece, chosen_move, chosen_take, current_board_copy, self.size)   
                new_hash = hash_board(new_board, self.size, self.hash_table)  
                action_hash.append(new_hash)                
                                
                # save the original position of the piece taking the action 
                # and the row of the action
                actions_to_take.append([chosen_piece, chosen_move, chosen_take])
                
        # retrieve the Q_values for the possible states        
        Q_val = np.zeros(len(action_hash))  
        
        for idx, hash_num in enumerate(action_hash):
        
            # calculate Q value        
            try: Q_val[idx] = self.values[hash_num] + self.UCB * math.sqrt(math.log(self.plays[current_hash]) / self.plays[hash_num])  
            
            # if self.plays[current_hash] = 0
            except ValueError:
                Q_val[idx] = self.values[hash_num] + self.UCB * math.sqrt(math.log(1) / self.plays[hash_num]) 
                self.plays[current_hash] = 1
                self.values[current_hash] = 0
            
        # choose the action
        if player == 'white':
            action = np.argmax(Q_val)
            
        elif player == 'black':
            action = np.argmin(Q_val)
        
        # return the chosen_piece, chosen_move, chosen_take
        return actions_to_take[action][0], actions_to_take[action][1], actions_to_take[action][2]
    
    
    """
    Backpropagate through the network update the history based 
    on the outcomes of self play.
    """
    def backpropagate(self, outcome):
        
        # take the most recent state
        last_board_hash = self.history.pop()
        self.plays[last_board_hash] += 1
        self.values[last_board_hash] = outcome
        
        # update using an average
        for hash_val in self.history: 
            self.plays[hash_val] += 1
            self.values[hash_val] += 1 / self.plays[hash_val] * (outcome - self.values[hash_val])       
    
    
    """
    Check if the player is going to enter any new states.
    """    
    def new_playable_states(self, possible_moves, pieces_taken, current_board, player):
        
        previously_visited = list()
        new_moves = dict()
        new_pieces_taken = dict()
            
        # cycle through positions with available moves
        for key, value in possible_moves.items():

            # cycle through the possible moves at that position
            for i in range(value.shape[0]):

                # create a copy of the array to avoid editing the original
                current_board_copy = current_board.copy()

                chosen_piece = key
                chosen_move = value[i, :]
                chosen_take = []

                if key in pieces_taken:
                    chosen_take = pieces_taken[key][i]     

                # get the new state and hash it
                new_board = update_board(player, chosen_piece, chosen_move, chosen_take, current_board_copy, self.size)   
                new_hash = hash_board(new_board, self.size, self.hash_table)  
                
                # check if the hash state is in the previous plays
                old_visit = new_hash in self.plays
                previously_visited.append(old_visit) 
                
                # save the new moves
                if not old_visit: 
                    
                    # if this is the first move for that piece                    
                    if chosen_piece not in new_moves:
                        new_moves[chosen_piece] = np.vstack([chosen_move])
                        
                        # if pieces were taken
                        if len(chosen_take) > 0:                            
                            new_pieces_taken[chosen_piece] = [chosen_take]
                    
                    # if this is not the first move
                    else:
                        
                        # add this move to previous moves
                        new_moves[chosen_piece] = np.vstack([new_moves[chosen_piece], chosen_move]) 
                        
                        # if this piece could take other pieces
                        if chosen_piece in new_pieces_taken:    
                            new_pieces_taken[chosen_piece] = [new_pieces_taken[chosen_piece][0], chosen_take]
                            
                        # if this is the only take
                        elif len(chosen_take) > 0:
                            new_pieces_taken[chosen_piece] = [chosen_take]
        
        return all(previously_visited), new_moves, new_pieces_taken
    
    """
    Save the learned values as a pickle file
    """
    def save_values(self, filename):
        
        # save values dictionary        
        values = open("./values/values" + filename + ".pkl", "wb")
        pickle.dump(self.values, values)
        values.close()
        
        # save plays dictionary
        plays = open("./values/plays" + filename + ".pkl", "wb")
        pickle.dump(self.plays, plays)
        plays.close()
        
    """
    Load the pre-trained values from the pickle file
    """
    def load_values(self, filename):
        
        # load values dictionary 
        values = open("./values/values" + filename + ".pkl", "rb")
        values_dict = pickle.load(values)
        self.values = values_dict
        
        # load plays dictionary         
        plays = open("./values/plays" + filename + ".pkl", "rb")
        plays_dict = pickle.load(plays)
        self.plays = plays_dict 