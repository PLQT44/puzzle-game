# a generic hexagonal puzzle game
# allows to handle easily 3D hex

# imports
from itertools import cycle
import pygame
import exceptions as exc
import puzzles.puzzle_game

SCALE = 50

################################################################################
#                   GEOMETRY FUNCTIONS                                         #
################################################################################

def project_2D(coordinates, x_offset = 0, y_offset = 0) -> tuple[int, int]:
    # transform the 3D coordinates in 2D according to plan geometry
    # I take into account screen geometry
    # entry is 3-tuplet, output is 2-tuplet
    x = coordinates[0]
    y = coordinates[1]
    A: int = round(x_offset + SCALE*(x + y/2))
    B: int = round(y_offset - SCALE*(1.73*y/2))
    return (A,B)

################################################################################
#                           CLASSES                                            #
################################################################################

class HexPoint(puzzles.puzzle_game.GamePoint):
    # It is a GamePoint with 3D hex capacities

    Hx: int
    Hy: int
    Hz: int
    x_offset: int
    y_offset: int

    def update_2D(self):
        # when updating, I need to align 3D and 2D
        self.rect.center = project_2D(
            (
                self.Hx,
                self.Hy,
                self.Hz),
            self.x_offset,
            self.y_offset)

    def __init__(self, 
                 Hx=0, 
                 Hy=0, 
                 Hz=0, 
                 x_offset = 0, 
                 y_offset = 0):
        
        puzzles.puzzle_game.GamePoint.__init__(
            self, 
            x_offset,
            y_offset)

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

    def set_pos(self, point):
        self.x_offset = point.x_offset
        self.y_offset = point.y_offset

        self.Hx = point.Hx
        self.Hy = point.Hy
        self.Hz = point.Hz

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

    def flip(self, origin):    
        new_x = self.Hz - origin.Hy
        new_y = -self.Hy + 2*origin.Hy
        new_z = self.Hx + origin.Hy
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

    image: pygame.Surface
    rect: pygame.Rect
    radius: int
    
    def __init__(self, 
                 Hx=0, 
                 Hy=0, 
                 Hz=0, 
                 x_offset= 0, 
                 y_offset = 0, 
                 setting_list = [''], 
                 radius = 10): #x_offset and y_offset are the x, y center of the 3D origin point

        HexPoint.__init__(self,
                          Hx,
                          Hy,
                          Hz,
                          x_offset,
                          y_offset)
        
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
        self.image.set_alpha(255)
        self.image.fill((0,0,0,0))
        if (len(self.elements) != 0 and
            'attracted' in [element.status for element in self.elements]):
            pygame.draw.circle(
                self.image,
                (0,0,0,200),
                (25,25),
                1.5*self.radius)
        else :
            pygame.draw.circle(
                self.image,
                (0,0,0,200),
                (25,25),
                self.radius)

    def update(self, event_list=[]):
        puzzles.puzzle_game.GridPoint.update(self, event_list)
        HexPoint.update(self)
         
    def clone(self):
        return self.__class__(self.Hx, self.Hy, self.Hz, self.x_offset, self.y_offset, self.setting_list)
    
class PieceElement(HexPoint, puzzles.puzzle_game.PieceElement):

    def __init__(self,
                 setting,
                 Hx = 0,
                 Hy = 0,
                 Hz = 0,
                 x_offset = 0,
                 y_offset = 0):
        
        HexPoint.__init__(self,
                          Hx = Hx,
                          Hy=Hy,
                          Hz=Hz,
                          x_offset=x_offset,
                          y_offset=y_offset)
        
        puzzles.puzzle_game.PieceElement.__init__(self,
                                                  setting, x_offset, y_offset)
    
    def update(self):
        self.collision_rect.center = self.rect.center
        if self.status == 'base':
            self.image.set_alpha(255)
        elif self.status == 'installed':
            self.image.set_alpha(255)
        else:
            self.image.set_alpha(190)

    def flip(self, origin):
        HexPoint.flip(self, origin)
        puzzles.puzzle_game.PieceElement.flip(self)

class Piece(puzzles.puzzle_game.Piece):

    # compared to the SuperClass Piece, this one has
    # - rotation as a next unit move
    # - a simple checkfit
    # - an explicit generator based on moves from element to element

    origin: PieceElement

    def __init__(self,
                 setting,
                 deck_position_x = 0,
                 deck_position_y = 0,
                 piece_build_sequence = [],
                 local_move_list = []):
        
        super().__init__(setting,
                         deck_position_x, deck_position_y, piece_build_sequence=piece_build_sequence, local_move_list = local_move_list)
        
    def reinit_to_deck(self):
         # I local_move enough to come back to initial position
        for i in range(self.local_move_index, self.local_move_length):
            self.next_local_move()
        
        # I have to move everyone in 3D hex to origin
        self.translate((
            -self.origin.Hx, # type: ignore
            -self.origin.Hy, # type: ignore
            -self.origin.Hz)) # type: ignore
        
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
            
        self.translate((
            point.Hx-self.origin.Hx,
            point.Hy-self.origin.Hy,
            point.Hz-self.origin.Hz))

    def detach(self, target_status):
        super().detach(target_status)

        # I add : to move everyone in 3D hex to origin
        self.translate((
            -self.origin.Hx,
            -self.origin.Hy,
            -self.origin.Hz))

class Grid(puzzles.puzzle_game.Grid):

    def __init__(self, width=0, height=0, x_offset = 0, y_offset = 0, setting_list = [''], point_list = []):
        super().__init__(width, height, x_offset, y_offset, point_list)

###############################################################################
#                   THE GLOBAL CLASS                                          #
###############################################################################

class HexGame(puzzles.puzzle_game.PuzzleGame):
    pass