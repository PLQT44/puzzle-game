# puzzle game
# functions for solving a puzzle
# save as solving.py

# imports
import random
from itertools import permutations #needed for permutations of the deck
import pygame
import exceptions as exc
import star_game as game

def build_deck(pieces_dict, grid):
	#takes the current status of the grid and of the pieces_dictionary, and returns a list of pieces which are still not installed, for solving algorithm
	#pieces_dict is structured as {piece_name : piece}
	return [piece for piece in pieces_dict.values() if piece.status == 'base']

################################################################################
#					ULTIMATE RECURSION FUNCTIONS							   #
################################################################################

def recursive_pose(grid, deck, do_split = True, complete = True):

	#the core of the solving program. Tries to fill the grid with pieces in the deck. Returns the new grid and deck or exc.SolvingImpossibility if no solution is found

	free_grid = grid.free_points()
	if len(free_grid) == 0: #no more free points, cool!
		return grid, deck

	#I have free points, let's continue
	
	#A little bit of shuffling to change, then put the pieces that have points with their colours set at beginning
	random.shuffle(deck)
	set_colours_list = [point.colour for point in grid.sprites() if point.colour != '']
	deck.sort(key=lambda piece: piece.colour in set_colours_list, reverse = True)
				
	#first, let's split, to test if there are very small sub-grids, in which case we need to exit
	grid_list = grid_split(grid)
	sorted_grid_list = sorted(grid_list, key=lambda grid: len(grid)) #sort it
	
	#check if the number of free points is superior to the smallest piece, otherwise exit immediatly
	if len(sorted_grid_list[0]) < min([len(piece.sprites()) for piece in deck]):
		raise exc.SolvingImpossibility
	
	#shuffle the free_grid then sort it according to distance to installed_points
	installed_points = [point for point in grid if point.status == 'installed']
	random.shuffle(free_grid)
	free_grid.sort(key=lambda point: group_distance(point, installed_points))

	point_index = 0	
	current_point = free_grid[point_index] #let's start with first free point
	piece_index = 0
	current_piece = deck[piece_index] #take the first piece in the deck

	#choose a piece that is smaller than the free grid. If none, exit
	while_exit = False
	while not(while_exit):
		if len(free_grid) < len(current_piece.sprites()):
			if complete:
				while_exit = True
				raise exc.SolvingImpossibility
			else:
				piece_index += 1
				current_piece = deck[piece_index] #take the next piece in the deck
		else:
			while_exit = True
	
	#I chose a correct piece, let's put it in position
	current_piece.set_pos(current_point) #I place in first grid's free point
	
	#now is the main loop
	while_exit = False
	while not(while_exit):
		#try to put the current_piece on the grid
		success, fitting_points = current_piece.check_fit(grid)
		if success: #it fits!
			current_piece.attach(fitting_points)
			deck.remove(current_piece)
			#now let's enter next recursion level
			try :
				next_grid, next_deck = recursive_pose(grid, deck)
				return next_grid, next_deck
			except exc.SolvingImpossibility: #I didn't manage to solve the sub-grid
				current_piece.detach('base')
				deck.insert(piece_index, current_piece) #logically put the piece back in the deck
				#I need to make the next move for piece
				point_index, current_point = current_piece.next_move(point_index, free_grid)
				
		else: #if piece does not fit, I move to next possibility ; first rotate, then try to translate, then try with next piece
			point_index, current_point = current_piece.next_move(point_index, free_grid)
			
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

###############################################################################
# I need a set of NEIGHBOURING FUNCTIONS to handle split and speed up solving #
###############################################################################

def group_distance(anchor_point, point_list):
	if len(point_list) > 0:
		return min([anchor_point.distance(point) for point in point_list])
	else:
		return 0

def find_neighbour(anchor_point, grid):
	#I browse through the points of the grid to see if one is neighboring the given point
	for point in grid.sprites():
		if point.neighbouring(anchor_point):
			return point

	raise exc.NoNeighbour

def grid_split(target_grid, anchor_grid = None):
	# separates a grid in a list of independent sub-grids of free points
	#anchor_list is an grid containing points from which I try to expand in grid
	
	free_list = list(target_grid.free_points())
	remaining_points_number = len(free_list)

	if remaining_points_number == 0: #no free point, answer is null
		if anchor_grid is None:
			return []
		else:
			return [anchor_grid]

	else: #there are at least 1 free points in target_grid, I can evaluate neighbouring and start recursion
		result_grid = game.Grid(x_offset = target_grid.x_offset, y_offset = target_grid.y_offset)
		#let's concentrate on free points of target_grid
		for point in target_grid.sprites():
			if point.status == 'base':
				result_grid.add(point)
		
		if anchor_grid is None: #create the initial point to grow from
			anchor_grid = game.Grid(x_offset = target_grid.x_offset, y_offset = target_grid.y_offset, point_list = [free_list[0]])
		
		for anchor_point in anchor_grid.sprites():
			#anchor point is outside of grid	
			result_grid.remove(anchor_point)
			try: #let's try to find a neighbour to the anchor point
				neighbour = find_neighbour(anchor_point, result_grid)
				#if I find a neighbour, I start recursing, anchoring in that neighbour
				anchor_grid.add(neighbour)
				result_grid.remove(neighbour)
				result = grid_split(result_grid, anchor_grid)
				return result
				
			except exc.NoNeighbour: #anchor_point has no neighbour --> I will check with another point in anchor_grid. If all anchor points have been tried, I have an independant grid
				pass
		
		#no point in anchor grid has a neighbour in result_grid
		result = [anchor_grid] + grid_split(result_grid)
		return result