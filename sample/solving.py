# puzzle game
# functions for solving a puzzle
# save as solving.py

# imports
import random
from itertools import permutations #needed for permutations of the deck
import pygame
import numpy as np
import exceptions as exc


def grid_to_array(grid):
     pass

def array_to_grid(array_grid):
    pass

def  index_to_cube(index):
    """Transcribes an array of index coordinates (row,column) into an array of (q,r,s) indexes, for use with a grid or piece map types

    Arguments:
        index -- a numpy array of indices. Shape is (2,n) : [[row1, row2, ...], [column1, column2, ...]]

    Returns:
        a numpy array of cube coordinates. Shape is (3, n) [[q1, q2, ...], [r1,r2,...], [s1, s2, ...]]

    """
    r: int=index[0]
    q: int=index[1]-np.floor_divide(r,2)
    s: int=-r-q
    
    return np.array((q,r,s))

def cube_to_index(cube):
    """Transcribes an array of cube coordinates (q,r,s) into an array of (row,column) indexes, for use with a grid or piece map types

    Arguments:
        cube -- a numpy array of cube coordinates. Shape is (3, n) [[q1, q2, ...], [r1,r2,...], [s1, s2, ...]]

    Returns:
        a numpy array of indices. Shape is (2,n) : [[row1, row2, ...], [column1, column2, ...]]
    """
    
    i= cube[1]
    j= cube[0] + np.floor_divide(i,2)
    
    return np.array(((i,j)))

def array_check_fit(array_grid, array_piece, index):
    """check whether a piece can be attached on a grid at index position

    Arguments:
        array_grid -- a play grid described as an numpy array
        array_piece -- a play piece described as a numpy array.
        index -- the position of the grid point where you are currently posing the piece. Should be in form [row, column]

    Returns:
        a boolean representing if the piece fits
    """
    end_index= index+array_piece.shape[1:3]
    
    return ~(array_grid[...,index[0]:end_index[0],index[1]:end_index[1]] * array_piece).any()

def array_pose(array_grid, array_piece, index):
    """attach a piece on a grid at index position

    Arguments:
        array_grid -- a play grid described as an numpy array
        array_piece -- a play piece described as a numpy array.
        index -- the position of the grid point where you are currently posing the piece. Should be [row, column]

    Returns:
        the grid with the piece attached on index position
    """
    end_index= index+array_piece.shape[1:3]
    array_grid[...,index[0]:end_index[0],index[1]:end_index[1]] += array_piece
    
    return array_grid

def array_depose(array_grid, array_piece, index):
    """detach a piece from a grid at the given index position

    Arguments:
        array_grid -- a play grid described as an numpy array
        array_piece -- a play piece described as a numpy array.
        index -- the position of the grid point where you are currently posing the piece

    Returns:
        the grid with the piece removed from "index" position
    """
    end_index= index+array_piece.shape[1:3]
    array_grid[...,index[0]:end_index[0],index[1]:end_index[1]] -= array_piece
    
    return array_grid

def array_next_point(array_grid, array_piece, index):
    """give the next point on the grid where to process (test, pose, depose) a piece

    Arguments:
        array_grid -- a play grid described as an numpy array
        array_piece -- a play piece described as a numpy array.
        index -- the position of the grid point where you are currently posing the piece

    Raises:
        FinalMove: if current index is the last possible point of the grid, raise this exception

    Returns:
        the index of the next point in the grid
    """
    if index[0]+array_piece.shape[-2] == array_grid.shape[-2]:
        if index[1]+array_piece.shape[-1] == array_grid.shape[-1]:
            raise FinalMove
        return np.array((0, index[1]+1))
    
    return index+np.array((1,0))

def cube_rotate(cube):
    return -np.roll(cube, shift=-1, axis=0)
    
def array_rotate(array_piece):
    piece_indices = np.array(np.nonzero(array_piece.sum(axis=0)))
    rotated_piece_indices=cube_to_index(cube_rotate(index_to_cube(piece_indices)))
    ranges = np.ptp(rotated_piece_indices, axis=1)
    rotated_piece_indices -= np.min(rotated_piece_indices, axis=1)[:,np.newaxis]
    
    rotated_piece=np.zeros(ranges+1, dtype=int)*np.ones((array_piece.shape[0],1,1), int)
    rotated_piece[:,
                  rotated_piece_indices[0],
                  rotated_piece_indices[1]]=array_piece[:,
                                                        piece_indices[0],
                                                        piece_indices[1]]
    return np.roll(rotated_piece, shift=1, axis=0)

def cube_flip(cube):
    cube[[0,2],:]=cube[[2,0],:]
    return cube

def array_flip(array_piece):
    piece_indices = np.array(np.nonzero(array_piece.sum(axis=0)))
    
    flipped_piece_indices=cube_to_index(cube_flip(index_to_cube(piece_indices)))
    ranges = np.ptp(flipped_piece_indices, axis=1)
    flipped_piece_indices -= np.min(flipped_piece_indices, axis=1)[:,np.newaxis]
    
    flipped_piece=np.zeros(ranges+1, dtype=int)*np.ones((array_piece.shape[0],1,1), int)
    flipped_piece[:,
                  flipped_piece_indices[0],
                  flipped_piece_indices[1]]=array_piece[:,
                                                        piece_indices[0],
                                                        piece_indices[1]]
    
    return np.flip(flipped_piece, axis=0)



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

