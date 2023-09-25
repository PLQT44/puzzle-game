# a generic hexagonal puzzle game
# allows to handle easily 3D hex

# imports
from itertools import cycle
import tkinter
import pygame
import exceptions as exc
import puzzles.puzzle_game

SCALE = 50

################################################################################
#                   GEOMETRY FUNCTIONS                                         #
################################################################################

def project_2D(coordinates, x_offset = 0, y_offset = 0):
    # transform the 3D coordinates in 2D according to plan geometry
    # I take into account screen geometry
    # entry is 3-tuplet, output is 2-tuplet
    x = coordinates[0]
    y = coordinates[1]
    A = x_offset + SCALE*(x + y/2)
    B = y_offset - SCALE*(1.73*y/2)
    return (A,B)

################################################################################
#                           CLASSES                                            #
################################################################################

class HexPoint(puzzles.puzzle_game.GamePoint):
    # It is a GamePoint with 3D hex capacities

    def update_2D(self):
        # when updating, I need to align 3D and 2D
        self.rect.center = project_2D((self.Hx, self.Hy, self.Hz), self.x_offset, self.y_offset)

    def __init__(self, Hx=0, Hy=0, Hz=0, x_offset = 0, y_offset = 0):
        puzzles.puzzle_game.GamePoint.__init__(self, x_offset, y_offset)

        # Each point has three 3D coordinates in Hexagonal plan.
        # Default creation is origin
        self.Hx = Hx
        self.Hy = Hy
        self.Hz = Hz
        self.update_2D()

    def set_2D(self, x, y):
        self.x_offset = x
        self.y_offset = y
        self.update_2D()

    def translate_e(self, distance = 1):
        #translate point to the east
        self.Hx += distance
        self.Hz += distance
        self.update_2D()

    def translate_ne(self, distance = 1):
        #translate point to the north-east
        self.Hy += distance
        self.Hz += distance
        self.update_2D()

    def translate_nw(self, distance = 1):
        #translate point to the north-west
        self.Hx += -distance
        self.Hy += distance
        self.update_2D()

    def translate_w(self, distance = 1):
        #translate point to the east
        self.Hx += -distance
        self.Hz += -distance
        self.update_2D()

    def translate_sw(self, distance = 1):
        #translate point to the north-east
        self.Hy += -distance
        self.Hz += -distance
        self.update_2D()

    def translate_se(self, distance = 1):
        #translate point to the north-west
        self.Hx += distance
        self.Hy += -distance
        self.update_2D()

    def translate(self, vector = (0,0,0)):
        #add vector to point
        self.Hx += vector[0]
        self.Hy += vector[1]
        self.Hz += vector[2]
        self.update_2D()

    def rotate(self, rotation_center):
        #rotates point around rotation_center by Pi/3, trigonometric direction
        #rotation_center is just another HexPoint
        new_x = - self.Hy + rotation_center.Hy + rotation_center.Hx
        new_y = self.Hx + self.Hy - rotation_center.Hx
        new_z = new_x + new_y
        self.Hx = new_x
        self.Hy = new_y
        self.Hz = new_z
        self.update_2D()

    def distance(self, point):
        #well, it is the square of distance in 3D hex space...
        return (abs(self.Hx-point.Hx) + abs(self.Hy-point.Hy) + abs(self.Hz-point.Hz))

    def neighbouring(self, point):
        return (self.distance(point) == 2)

    def update(self):
        self.update_2D()

    def clone(self):
        return HexPoint(self.Hx, self.Hy, self.Hz, self.x_offset, self.y_offset)

class GridPoint(HexPoint, puzzles.puzzle_game.GridPoint):
    # this is a point for a grid. I define it as a subclass of HexPoint and of GridPoint

    def __init__(self, 
                 Hx=0, 
                 Hy=0, 
                 Hz=0, 
                 x_offset= 0, 
                 y_offset = 0, 
                 setting_list = [''], 
                 radius = 10): #x_offset and y_offset are the x, y center of the 3D origin point

        HexPoint.__init__(self, Hx, Hy, Hz, x_offset, y_offset)
        puzzles.puzzle_game.GridPoint.__init__(self, 
                                               x_offset, 
                                               y_offset, 
                                               setting_list)

        # Create a surface for the sprite - a 50*50 square with a black circle
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        self.image.fill((255, 255, 255, 0))	 # Fill with transparent white

        #set the radius
        self.radius = radius

        #add a circle
        pygame.draw.circle(self.image, (0,0,0,255), (25,25), radius)

        # Set the sprite's rect (position and size)
        self.rect = self.image.get_rect()
        self.update_2D()
    
    def display_update(self):
        pass #this one is really game-dependant

    def update(self, event_list=[]):
        puzzles.puzzle_game.GridPoint.update(self,event_list)
        HexPoint.update(self)
         
    def clone(self):
        return self.__class__(self.Hx, self.Hy, self.Hz, self.x_offset, self.y_offset, self.setting_list)
    
class PieceElement(HexPoint, puzzles.puzzle_game.PieceElement):

    def __init__(self, setting, Hx = 0, Hy = 0, Hz = 0, x_offset = 0, y_offset = 0):
        HexPoint.__init__(self, Hx, Hy, Hz, x_offset, y_offset)
        puzzles.puzzle_game.PieceElement.__init__(self, setting, x_offset, y_offset)
        
    def update(self):
        if self.status == 'base':
            self.image.set_alpha(255)
        elif self.status == 'installed':
            self.image.set_alpha(192)
        else:
            self.image.set_alpha(128)

class Piece(puzzles.puzzle_game.Piece):

    # compared to the SuperClass Piece, this one has
    # - rotation as a next unit move
    # - a simple checkfit
    # - an explicit generator based on moves from element to element

    def __init__(self, setting, 
              deck_position_x = 0, 
              deck_position_y = 0, 
              build_sequence = [], local_move_list = []):
        super().__init__(setting, deck_position_x, deck_position_y, build_sequence=build_sequence, local_move_list = local_move_list)
    
    def rotate(self):
        for element in self.sprites():
            element.rotate(self.origin)
    
    def reinit(self):
        # I set local_move_index to 0
        for i in range(self.local_move_index, self.local_move_length):
            self.local_unit_move(self.local_move_list[i])
        
        self.local_move_index = 0

        # I have to move everyone in 3D hex to origin
        vector = (-self.origin.Hx, -self.origin.Hy, -self.origin.Hz)
        self.translate(vector)

    def reinit_to_deck(self):
        self.reinit()
        super().reinit_to_deck()
        self.update_2D()

    def update_2D(self):
        for element in self.sprites():
            element.update_2D()

    def set_pos(self, point):
        # I have to move everyone in 3D hex to the point's coordinates
        for element in self.sprites():
            element.x_offset = point.x_offset
            element.y_offset = point.y_offset
            
        vector = (point.Hx-self.origin.Hx, point.Hy-self.origin.Hy, point.Hz-self.origin.Hz)
        self.translate(vector)

    def local_unit_move(self, local_move=''):
        pass #should be game_dependant

    def detach(self, target_status):
        super().detach(target_status)

        # I add : to move everyone in 3D hex to origin
        vector = (-self.origin.Hx, -self.origin.Hy, -self.origin.Hz)
        self.translate(vector)

class Grid(puzzles.puzzle_game.Grid):

    def __init__(self, width=0, height=0, x_offset = 0, y_offset = 0, setting_list = [''], point_list = []):
        super().__init__(width, height, x_offset, y_offset, point_list)

###############################################################################
#                   THE GLOBAL CLASS                                          #
###############################################################################

class HexGame(puzzles.puzzle_game.PuzzleGame):

    def __init__(self, name, caption, icon_path, setting_list, pieces_generator):
        super().__init__(name, caption, icon_path, setting_list, pieces_generator)

    def build_grid(self, grid_width, grid_height, x_offset, y_offset, setting_list):
        self.grid = Grid(grid_width, grid_height, x_offset, y_offset, setting_list) 

    def build_pieces(self, pieces_generator, piece_class):
        super().build_pieces(pieces_generator, piece_class)