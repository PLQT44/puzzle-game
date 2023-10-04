# src/puzzles/star_game.py

# Marie-Aimee's bubble puzzle
# it is a subclass of HexGame
# it needs multi-piece on a grid point 

# imports
from itertools import cycle
import tkinter
import numpy
import pygame
import exceptions as exc
import puzzles.hex_game
from constants import RGB_COLOURS

################################################################################
#                          CONSTANTS                                           #
################################################################################

GRID_WIDTH = 6
GRID_HEIGHT = 4
SCALE = 50
PIECES_GENERATOR = { 'light_green' : [['in', 'e', 'e'], ['out', '', 'e'], ['out', 'nw', '']],
                    'lagoon' : [['in', 'e', 'e'], ['out', '', 'e'], ['out', 'ne', '']],
                    'yellow' : [['out', 'w', 'e'], ['out', '', 'ne'], ['out', 'nw', '']],
                    'purple' : [['out', 'se', 'e'], ['out', '', 'ne'], ['in', 'sw', '']], 
                    'light_blue' : [['out', 'nw', 'e'], ['out', '', 'ne'], ['in', 'sw', '']],
                    'pink' : [['in', 'e', 'e'], ['out', '', 'ne'], ['out', 'w', '']],
                    'orange' : [['in', 'e', 'e'], ['out', 'e', 'nw'], ['in', 'se', '']],
                    'green' : [['in', 'e', 'e'], ['in', 'nw,w', 'nw'], ['out', 'nw', '']],
                    'blue' : [['in', 'e', 'e'], ['in', 'nw,w', 'nw'], ['out', 'w', '']],
                    'red' : [['in', 'e', 'e'], ['out','se', 'nw'], ['out', 'e', '']],
                    'fuchsia' : [['in', 'e','e'], ['out', 'sw', 'ne'], ['in', 'sw', '']],
                    'violet' : [['in', 'e', 'e'], ['out', 'nw,ne', 'e'], ['in', 'w', '']]
                    }
SETTING_LIST = [''] 
ANGLE_DICT = {'e': 0, 'ne':60, 'nw': 120, 'w': 180, 'sw':240, 'se':300}
LOCAL_MOVE_LIST = ['r', 'r', 'r', 'r', 'r','r,f', 'r', 'r','r', 'r','r','r,f']
ICON_PATH = './images/bubble_pink_out_.png'

################################################################################
#                           CLASSES                                            #
################################################################################

class GridPoint(puzzles.hex_game.GridPoint):
    
    def match_neighbour_direction(self, point): 
        #to be further detailed. this is needed when self surrounded by 'out'pieces
        # and I want to check if the element on "point" is correctly oriented
        return True
    
    def is_free(self):
                
        if len(self.elements) == 2: # 2 pieces on this point, it is not free
            return False
        
        if len(self.elements) == 0: # no piece on the element, it is free (but may be alone)
            return True
        
        if len(self.elements[0].out_directions) == 0: # this is a piece with no way out
            return False
        
        return True
    
    def neighbouring(self, point):
        #first, let's check distance
        if not super().neighbouring(point):
            return False

        if not (self.is_free() and point.is_free()):
            return False

        vector_dict = { (1,0,1) : 0,
                           (0,1,1) : 60,
                           (-1,1,0):120,
                           (-1,0,-1):180,
                           (0,-1,-1):240,
                           (1,-1,0):300}

        vector = (point.Hx-self.Hx, point.Hy-self.Hy, point.Hz-self.Hz)
        vector_angle = vector_dict[vector]
        
        if len(self.elements) == 0:
            if len(point.elements) == 0:
                return True # 2 free points, easy one
            
            if point.elements[0].type == 'out' and all((vector_angle in [(direction-60)%360, direction, (direction+60)%360]) for direction in point.elements[0].out_directions):
                return False # point's element is 'out' type, turning its back to self
            
            return True # either point's element is 'out' type facing correctly, or 'in' type, which is OK

        if self.elements[0].type == 'out':
            if not any((vector_angle in [(direction-60)%360, direction, (direction+60)%360]) for direction in self.elements[0].out_directions ):
                return False #the point must be aligned +/- 60 degrees with self's overture
            
            if len(point.elements) == 0:
                return True # self's element is 'out' type pointing correctly, and point is free
            
            if point.elements[0].type == 'out':
                if any(any(((self_direction + point_direction -2*vector_angle)%360 == 180)
                              for point_direction in point.elements[0].out_directions)
                                for self_direction in self.elements[0].out_directions ):
                    return True # two 'out' elements set in a triangle
                else:
                    return False          
                  
            # point's element is 'in' type
            if any((self_direction == vector_angle) for self_direction in self.elements[0].out_directions):
                return True #if the points are aligned with self's element overture, it is OK

            # self's overture is now 60 degrees from vector
            if len(point.elements[0].out_directions) == 2:
                return False # it doesn't work if point's element is a 2-direction "in" type
            
            if any(((self_direction + point.elements[0].out_directions[0] - 2*vector_angle)%360 in [0,300]) for self_direction in self.elements[0].out_directions):
                return True # there are only two possible relative directions if point's element is "in" type
            
            return False
        
        # Now I know that self's element is "in" type
        if len(point.elements) == 0:
            return True # point is free
        
        if point.elements[0].type == 'out':
            if all((vector_angle in [(direction-60)%360, direction, (direction+60)%360]) for direction in point.elements[0].out_directions):
                return False # point's element is 'out' type turning its back to self

            if any(((point_direction - vector_angle)%360 == 180) for point_direction in point.elements[0].out_directions):
                return True # point's element is 'out' type, facing directly self
            
            #now point is 'out' type facing self with 60 degrees
            if len(self.elements[0].out_directions) == 2:
                return False # it doesn't work if self's element is a 2-direction "in" type
            
            if any(((point_direction + self.elements[0].out_directions[0] - 2*vector_angle)%360 in [0,60]) for point_direction in point.elements[0].out_directions):
                return True # there are only two possible relative directions if point's element is "in" type
        
        # now point's element is also 'in' type
        if len(self.elements[0].out_directions) == 2 or len(point.elements[0].out_directions) == 2:
            return False # it doesn't work with 2_directions 'in' type elements. In fact only red piece can connect the two points
        
        if (((self.elements[0].out_directions[0] - vector_angle)%360 in [60, 180, 300])
            and ((self.elements[0].out_directions[0] - point.elements[0].out_directions[0])%360 in [60,300])):
            return True # these are the only configurations where it works 

        return False
    
class PieceElement(puzzles.hex_game.PieceElement):
    
    def __init__(self, colour, element_build_sequence = ['in', '', ''], x_offset = 0, y_offset = 0):
        super().__init__(colour, x_offset, y_offset)

        #I need a type ('in' or 'out'), for check fit later
        self.type = element_build_sequence[0]

        #I need a rotation indicator
        self.rotation_status = 0

        # I specify outgoing directions
        self.out_directions = [ANGLE_DICT[direction] for direction in element_build_sequence[1].split(',') if direction != '']

        # create image 
        self.reference_image = get_bubble_image(colour, element_build_sequence)
        self.image = self.reference_image

        # Set the sprite's rect (position and size)
        self.rect = self.image.get_rect()
        self.update_2D()
        center_point = self.rect.center
        self.collision_rect = pygame.Rect((center_point[0] - 20, center_point[1] - 20), (40, 40))
        
    def rotate(self, rotation_center):
        super().rotate(rotation_center)
        
        center_point = self.rect.center

        self.rotation_status = (self.rotation_status + 1) % 6
        self.image = pygame.transform.rotate(self.reference_image, 60 * self.rotation_status)
        self.rect = self.image.get_rect(center = center_point)

        new_rect = pygame.Rect(((self.rect.width-50)/2, (self.rect.height-50)/2),(50,50))

        self.image = self.image.subsurface(new_rect)
        self.rect = self.image.get_rect(center = center_point)

        self.out_directions = [((direction + 60) % 360) for direction in self.out_directions]
        
    def flip(self, origin):
        self.reference_image = pygame.transform.flip(self.reference_image,0,1)
        self.image = self.reference_image
        self.out_directions = [((360-direction) % 360) for direction in self.out_directions]
        super().flip(origin)
        self.rect = self.image.get_rect(center = self.rect.center)
    
    def matching(self, point):
        if self in point.elements:
            return True
        if len(point.elements) == 0:
            return True
        if len(point.elements) > 1:
            return False
        if point.elements[0].type == self.type:
            return False
        if point.elements[0].match_directions(self):
            return True
        return False

    def match_directions(self, element):
        # the function is called only if the two elements have different types
        if (len(self.out_directions) == 0) or (len(element.out_directions) == 0):
            return False

        if self.type == 'out':
            return element.match_directions(self) #self must be of type 'in'

        return all((self_direction in element.out_directions)
                for self_direction in self.out_directions)         

class Piece(puzzles.hex_game.Piece):
    
    def __init__(self,
                 colour,
                 deck_position_x = 0,
                 deck_position_y = 0,
                 piece_build_sequence = [],
                 local_move_list = LOCAL_MOVE_LIST):
        
        super().__init__(colour, deck_position_x, deck_position_y, piece_build_sequence = piece_build_sequence, local_move_list = local_move_list)

        anchor_point = puzzles.hex_game.HexPoint(x_offset=deck_position_x, y_offset=deck_position_y)

        # Add first element to the group
        piece_element = PieceElement(colour,
                                    piece_build_sequence[0],
                                    x_offset = deck_position_x,
                                    y_offset = deck_position_y)
        self.add(piece_element)
        self.origin = piece_element


        for i in range(1,3):
            #translate anchor point
            getattr(anchor_point, "translate_" + piece_build_sequence[i-1][2])()
            piece_element = PieceElement(colour,
                                         piece_build_sequence[i],
                                         x_offset=deck_position_x,
                                         y_offset=deck_position_y)
            piece_element.set_pos(anchor_point)
            self.add(piece_element)

        self.compute_rect()

    def flip(self):
        for element in self.sprites():
            element.flip(self.origin)

    def local_unit_move(self, local_move):
        self.rotate()
        if 'f' in local_move:
            self.flip()
        super().local_unit_move()
    
    def matching_points(self, grid):
        # just returns the dictionary of matching points which may be OK; keys are PieceElements, values are GridPoints 

        # let's test and handle collisions!
        collide_dict = pygame.sprite.groupcollide(
            self, grid, False, False, pygame.sprite.collide_rect_ratio(0.3))

        # remove occupied points
        proper_dict = {}
        for element, point_list in collide_dict.items():
            for point in point_list:
                if element.matching(point):
                    proper_dict[element] = point

        return proper_dict

    def check_fit(self, grid):
        # test collision with the grid, returns a success boolean and a dictionary of attachment points
        points_dict = self.matching_points(grid)
        
        # let's check if the whole piece fits in
        return all((element in points_dict.keys()) for element in self.sprites()), points_dict
    
    def is_clicked_piece(self, event):
        if not any(sprite.collision_rect.collidepoint(event.pos) for sprite in self.sprites()):
            return False
        selected_sprite = next(filter(lambda element: element.collision_rect.collidepoint(event.pos), self.sprites()))
        if selected_sprite.grid_point == None:
            return True
        return ((len(selected_sprite.grid_point.elements) == 1) or 
                ((len(selected_sprite.grid_point.elements) == 2) and
                 (selected_sprite.type == 'in')))
        
class Grid(puzzles.hex_game.Grid):

    def __init__(self, width=0, height=0, x_offset = 0, y_offset = 0, setting_list = [''], point_list = []):
        super().__init__(width, height, x_offset, y_offset, setting_list, point_list)

        for Y in range(height):
            P = GridPoint(x_offset = x_offset, y_offset = y_offset, setting_list = setting_list) #initiate point at origin

            P.translate_nw(Y)

            if Y % 2 == 0:
                P.translate_e(round(Y/2))
            else:
                P.translate_e(round((Y-1)/2))
            
            self.add(P)

            for X in range(width):
                new_P = P.clone()
                new_P.translate_e()
                self.add(new_P)
                P = new_P

            P.kill()

################################################################################
#                    BUILDING FUNCTIONS                                        #
################################################################################

def get_bubble_image(name = 'black', element_build_sequence = ['in', '', '']):
    return pygame.image.load(f"./images/bubble_{name}_{element_build_sequence[0]}_{element_build_sequence[1]}.png")

###############################################################################
#                   THE GLOBAL CLASS                                          #
###############################################################################

class BubbleGame(puzzles.hex_game.HexGame):

    def __init__(self):
        super().__init__("BubbleGame", "Bubble Puzzle", ICON_PATH, SETTING_LIST, PIECES_GENERATOR)
        self.complete_game = False

    def build_grid(self):
        self.grid = Grid(GRID_WIDTH, GRID_HEIGHT, 0, 0, SETTING_LIST)

    def build_pieces(self, generator):
        super().build_pieces(generator, Piece)

    # def solve(self, surface):
    #     self.build_deck(self.pieces_dict)
    #     self.deck.sort(key=lambda piece: sum(len(element.out_directions) for element in piece.sprites()), reverse=True)
    #     self.recursive_pose(surface)

    
