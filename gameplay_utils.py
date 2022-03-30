#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 18:47:54 2022

@author: hemerson
"""

from board import Board
from agent import Random_Actor

import time


"""
Train Monte Carlo Tree Search via Self-Play
"""
def train_mcts(mcts_agent, max_games, max_moves, size, save_filename, load_filename=None, debug=False):
    
    agent_white = mcts_agent(player='white', size=size)    
    agent_black = mcts_agent(player='black', size=size)   
    
    if load_filename != None:
        print('Data loaded from plays{0}.pkl and values{0}.pkl'.format(load_filename))
        agent_white.load_values(filename=load_filename)
    
    for game in range(1, max_games + 1):
        
        print('Game {}'.format(game))
        board = Board(size=size) 
        
        for mov in range(max_moves):
            
            if (mov + 1) % 10 == 0: print('Move {}'.format(mov))
            
            # get the possible moves for white
            possible_actions, possible_takes = board.get_moves('white')
            if len(possible_actions) == 0:
                print('Game {}: Black/Red wins'.format(game))
                break    
            
            if debug: tic = time.perf_counter()
            
            # select an action and update the board
            chosen_piece, chosen_move, chosen_take = agent_white.select_action(possible_actions, possible_takes, board.data)
            board.update('white', chosen_piece, chosen_move, chosen_take) 
            
            if debug:
                toc = time.perf_counter() 
                print('Selecting action: {}s'.format(toc - tic))  
            
            # share knowledge between players
            agent_black.values = agent_white.values
            agent_black.plays = agent_white.plays
            
            # get the possible moves for black
            possible_actions, possible_takes = board.get_moves('black')
            if len(possible_actions) == 0:
                print('Game {}: White/Gray wins'.format(game))
                break                  
            
            # select an action to update the board
            chosen_piece, chosen_move, chosen_take = agent_black.select_action(possible_actions, possible_takes, board.data)
            board.update('black', chosen_piece, chosen_move, chosen_take)  
            
            # share knowledge between players
            agent_white.values = agent_black.values
            agent_black.plays = agent_white.plays
            
            # terminate when max moves exceeded
            if mov == (max_moves - 1):
                print('Game {}: Stalemate'.format(game))   
                break        
        
        # save dictionary
        agent_white.save_values(filename=save_filename)
        print('Performed {} moves'.format(len(agent_white.values)))


"""
Play a single game between two specified agents 
and visualise the results.
"""
def play_game(agent_white, agent_black, board, max_moves, visual="terminal"):
    
    for mov in range(max_moves):
        
        print('Move: {} ---------------------------\n'.format(2* mov + 1))
        
        # white player moves ------------------------
        board.show_board(visual=visual)
        
        possible_actions, possible_takes = board.get_moves('white')
        
        if len(possible_actions) == 0:
            print('Black/Red has won the game!')
            break     
            
        chosen_piece, chosen_move, chosen_take = agent_white.select_action(possible_actions, possible_takes, board.data)
        print('White moves {} to {}\n'.format(chosen_piece, (chosen_move[0], chosen_move[1])))
        board.update('white', chosen_piece, chosen_move, chosen_take)     
        
        #--------------------------------------------- 
        
        print('Move: {} ---------------------------\n'.format(2*mov + 2))
        
        # black player moves ------------------------
        board.show_board(visual=visual)
        
        possible_actions, possible_takes = board.get_moves('black')
        
        if len(possible_actions) == 0:
            print('White/Gray has won the game!')
            break        
        
        chosen_piece, chosen_move, chosen_take = agent_black.select_action(possible_actions, possible_takes, board.data)
        print('Black moves {} to {}\n'.format(chosen_piece, (chosen_move[0], chosen_move[1])))
        board.update('black', chosen_piece, chosen_move, chosen_take)     
        
        #---------------------------------------------      
        
        if mov == (max_moves - 1):
            print('The game has ended as a stalemate!')
            break
            
"""
Play a single game against a specified player with a 
human acting as the black player.
"""            
def play_player(agent_white, board, max_moves, visual="terminal"):
    
    agent_black = Random_Actor('black')
    
    for mov in range(max_moves):
        
        print('Move: {} ---------------------------\n'.format(2* mov + 1))
        
        # white player moves --------------------------
        board.show_board(visual=visual)
        
        possible_actions, possible_takes = board.get_moves('white')
        
        if len(possible_actions) == 0:
            print('Black/Red has won the game!')
            break     
            
        chosen_piece, chosen_move, chosen_take = agent_white.select_action(possible_actions, possible_takes, board.data)
        print('White/Gray moves {} to {}\n'.format(chosen_piece, (chosen_move[0], chosen_move[1])))
        board.update('white', chosen_piece, chosen_move, chosen_take)     
        
        #------------------------------------------------
        
        print('Move: {} ---------------------------\n'.format(2*mov + 2))
        
        # black player moves  --------------------------
        board.show_board(visual=visual)
        
        possible_actions, possible_takes = board.get_moves('black')
        corrected_actions = agent_black.ensure_jump(possible_actions, possible_takes)
        
        if len(possible_actions) == 0:
            print('White/Gray has won the game!')
            break 
        
        print('Please select a move from the following actions:')
        print(corrected_actions)
        
        chosen_piece = None
        chosen_move = None
        move_chosen = False        
        chosen_take = []
        chosen_index = None
            
        while chosen_piece not in corrected_actions:
            print('\nSelect the piece to move')
            
            # convert string to tuple
            try: chosen_piece = tuple(map(int, input().split(', ')))
            except ValueError: pass
            
        while not move_chosen:
            print('\nSelect the row index for the move')
            try: chosen_index = int(input())
            except ValueError: continue
            
            if chosen_index <= corrected_actions[chosen_piece].shape[0] - 1 and chosen_index >= 0:
                
                chosen_move = corrected_actions[chosen_piece][chosen_index, :]
                
                if len(possible_takes) > 0:
                    chosen_take = possible_takes[chosen_piece][chosen_index]
                
                move_chosen = True

        print('Black/Red moves {} to {}\n'.format(chosen_piece, (chosen_move[0], chosen_move[1])))
        board.update('black', chosen_piece, chosen_move, chosen_take)     
        
        #------------------------------------------------
        
        if mov == (max_moves - 1):
            print('The game has ended as a stalemate!')
            break  