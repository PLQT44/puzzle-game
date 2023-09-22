# Anne-Marie Stars' puzzle

# imports
from itertools import cycle
import tkinter
import pygame
import exceptions as exc
import puzzles.puzzle_game
from constants import RGB_COLOURS

################################################################################
#                          CONSTANTS                                           #
################################################################################

GRID_WIDTH = 7
GRID_HEIGHT = 4
SCALE = 50
PIECES_GENERATOR = { "red" : ['ne', 'se', 'ne'], "green" : ['e', 'e', 'ne'], "pink" : ['ne', 'e', 'se'], "blue" : ['ne', 'se', 'e'], "yellow" : ['e', 'ne', 'se'], "violet" : ['e', 'e'], "orange" : ['e', 'ne']}
SETTING_LIST = [''] + list(PIECES_GENERATOR.keys())
LOCAL_MOVE_LIST = ['r', 'r', 'r', 'r', 'r','r']
ICON_PATH = './images/Star_icon_stylized.svg.png'


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
                 radius = 10): #x_offset and y_offset are the x, y of the 3D origin point

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
        if self.status == 'base':
            pygame.draw.circle(self.image, (0,0,0,255), (25,25), self.radius)
            self.image.set_alpha(255)  # non-transparent
        elif self.status == 'attracted':
            pygame.draw.circle(self.image, (0,0,0,128), (25,25), 1.5*self.radius)
            self.image.set_alpha(128) #semi transparent
        elif self.status == 'installed':
            self.image.set_alpha(0)
        
        if self.setting != '':		
            self.image = pygame.image.load("./images/star_" + self.setting + ".png")
            self.rect = self.image.get_rect()
            self.update_2D()
            self.image.set_alpha(128)

    def update(self, event_list=[]):
        puzzles.puzzle_game.GridPoint.update(self,event_list)
        HexPoint.update(self)
         
    def clone(self):
        return GridPoint(self.Hx, self.Hy, self.Hz, self.x_offset, self.y_offset, self.setting_list)
    
class PieceElement(HexPoint, puzzles.puzzle_game.PieceElement):
    # this is the basic constituent of a piece
    # it has a setting, which, in this game, is a colour
    # it has a status indicator indicating where the piece is: 'base', 'moving', 'attracted, 'installed'
    # it has a reference to its attachment grid_point when installed

    def __init__(self, setting, Hx = 0, Hy = 0, Hz = 0, x_offset = 0, y_offset = 0):
        HexPoint.__init__(self, Hx, Hy, Hz, x_offset, y_offset)
        puzzles.puzzle_game.PieceElement.__init__(self, setting, x_offset, y_offset)

        # Create a surface for the sprite - a star image
        self.image = pygame.image.load("./images/star_" + setting + ".png")

        # Set the sprite's rect (position and size)
        self.rect = self.image.get_rect()
        self.update_2D()
        
    def update(self):

        if self.status in ['base', 'installed']:
            self.image.set_alpha(255)
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
              build_sequence = [], local_move_list = LOCAL_MOVE_LIST):
        super().__init__(setting, deck_position_x, deck_position_y, build_sequence=build_sequence, local_move_list = local_move_list)

        # Add first element to the group
        piece_element_1 = PieceElement(setting, 
                                x_offset = deck_position_x,
                                y_offset = deck_position_y)
        self.add(piece_element_1)
        self.origin = piece_element_1

        # create elements based on build_sequence of moves
        ref_elt = piece_element_1
        for move in build_sequence:
            new_element = PieceElement(setting = ref_elt.setting,
                              Hx = ref_elt.Hx,
                              Hy = ref_elt.Hy,
                              Hz = ref_elt.Hz,
                              x_offset = ref_elt.x_offset,
                              y_offset = ref_elt.y_offset)
            method = getattr(new_element, "translate_" + move)
            method()
            self.add(new_element)
            ref_elt = new_element
        
        self.compute_rect()

    def rotate(self):
        for element in self.sprites():
            element.rotate(self.origin)
        
    def reinit(self):
        # I set local_move_index to 0
        rotate_range = -self.local_move_index%6 
        for i in range(rotate_range):
            self.rotate()
        
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
        vector = (point.Hx-self.origin.Hx, point.Hy-self.origin.Hy, point.Hz-self.origin.Hz)
        self.translate(vector)

        for element in self.sprites():
            element.x_offset = point.x_offset
            element.y_offset = point.y_offset

        self.update_2D()

    def local_unit_move(self, local_move=''):
        self.rotate()

    def detach(self, target_status):
        super().detach(target_status)

        # I add : to move everyone in 3D hex to origin
        vector = (-self.origin.Hx, -self.origin.Hy, -self.origin.Hz)
        self.translate(vector)

class Grid(puzzles.puzzle_game.Grid):

    def __init__(self, width=0, height=0, x_offset = 0, y_offset = 0, setting_list = [''], point_list = []):
        super().__init__(width, height, x_offset, y_offset, point_list)

        for Y in range(height):
            P = GridPoint(x_offset = x_offset, y_offset = y_offset, setting_list = setting_list) #initiate point at origin

            P.translate_nw(Y)

            if Y % 2 == 0:
                P.translate_e(round(Y/2))
                local_width = width-1  #even  rows are smaller
            else:
                P.translate_e(round((Y-1)/2))
                local_width = width

            self.add(P)

            for X in range(local_width):
                new_P = P.clone()
                new_P.translate_e()
                self.add(new_P)
                P = new_P

            P.kill()
                
    def normalize(self, attracted_points):
        #attracted_points is a dictionary of piece elements with attracted point
        #browse through the points, if point has status activated but not in the activated list, then back to 'base' status

        for grid_point in self.sprites():
            if (grid_point.status == 'attracted') and not(grid_point in attracted_points.values()):
                grid_point.status = 'base'

################################################################################
#                    BUILDING FUNCTIONS                                        #
################################################################################

def create_star_image(piece):
    # Read the elementary star Image
    # colour is a string
    image = tkinter.Image.open("./images/6_star_original_turned.png")

    #remove blank space around star
    #I start by setting all non-black pixels to transparent
    image = image.convert("RGBA")
    datas = image.getdata()
    new_image_data = []

    for item in datas:
        # change all non-black pixels to transparent white, and else pure black
        if item[-1] < 200: #non black pixel
            new_image_data.append((255,255,255,0)) #transparent white
        else:
            new_image_data.append((0,0,0,255)) #pure black

    # update image data
    image.putdata(new_image_data)
    image = image.crop(image.getbbox())

    # Resize the image using resize() method
    image = image.resize((50, 50))

    #let's change the colour
    colour = piece.colour
    image = image.convert("RGBA")
    datas = image.getdata()
    new_image_data = []

    for item in datas:
        # change all non-transparent pixels to colour, no transparency
        if item[-1] != 0:
            new_image_data.append((RGB_COLOURS[colour][0],
                                   RGB_COLOURS[colour][1],
                                   RGB_COLOURS[colour][2],
                                   255))
        else:
            new_image_data.append(item)

    # update image data
    image.putdata(new_image_data)
    # save new image
    image.save("./images/star_" + colour + ".png")

###############################################################################
#                   THE GLOBAL CLASS                                          #
###############################################################################

class StarGame(puzzles.puzzle_game.PuzzleGame):

    def __init__(self):
        super().__init__("StarGame", "Star Puzzle", ICON_PATH, SETTING_LIST, PIECES_GENERATOR)

    def build_grid(self):
        grid = Grid(GRID_WIDTH, GRID_HEIGHT, 0, 0, SETTING_LIST)
        return grid

    def build_pieces(self, generator):
        return super().build_pieces(generator, Piece)