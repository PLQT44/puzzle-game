# puzzle game
# functions for solving a puzzle
# save as solving.py

# imports
import random
from itertools import permutations #needed for permutations of the deck
import pygame
import exceptions as exc
import puzzles.star_game as game

################################################################################
#					ULTIMATE RECURSION FUNCTIONS							   #
################################################################################

			
###############################################################################
# I thought this next function was a good idea, but in fact it isn't, because I have to browse through all pieces. 
# anyway, was fun trying		
###############################################################################

def multi_recursive_pose(grid_list, deck):

	sorted_grid_list = sorted(grid_list, key=lambda grid: len(grid))
	first_sub_grid = sorted_grid_list.pop(0)
	while_exit = False
	possible_decks = permutations(deck)
	current_deck = list(next(possible_decks)) #start the iterator

	while not(while_exit):
		try:
			#if this is the last grid to solve, then first piece must fit
			if len(sorted_grid_list) == 0:
				complete = True
			else:
				complete = False
			
			next_deck = first_sub_grid.recursive_pose(current_deck, False, complete)
			
			#we need to try the rest of the grids. If it works, fine! else, we need to change the way to solve the first sub-grid, end try again. I do that by permutating the deck.
			try:
				if len(sorted_grid_list) == 0:
					return first_sub_grid, next_deck
				else:
					new_next_grid, new_next_deck = multi_recursive_pose(sorted_grid_list, next_deck)
					first_sub_grid.add(new_next_grid)
					return first_sub_grid, new_next_deck
			
			except exc.SolvingImpossibility: #couldn't solve the next grid with the way the first sub grid was solved
				first_sub_grid.reinit() #remove all pieces, set points to 'base' status
				try:
					current_deck = list(next(possible_decks)) #I start again with a permutated deck
				except StopIteration as e: #I tried all permutations of the deck, and the whole branch is, in fact, unsolvable
					while_exit = True

		except exc.SolvingImpossibility: 
			while_exit = True
	
	raise exc.SolvingImpossibility

