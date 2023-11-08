# Anne-Marie Stars' puzzle
# it is a subclass of HexGame

# imports
from itertools import cycle
import tkinter

import pygame_menu
import pygame
import exceptions as exc
import puzzles.hex_game
from constants import RGB_COLOURS

################################################################################
#                          CONSTANTS                                           #
################################################################################

GRID_WIDTH = 7
GRID_HEIGHT = 4
SCALE = 50
PIECES_GENERATOR = {
    "red" : ['ne', 'se', 'ne'],
    "green" : ['e', 'e', 'ne'],
    "pink" : ['ne', 'e', 'se'],
    "blue" : ['ne', 'se', 'e'],
    "yellow" : ['e', 'ne', 'se'],
    "violet" : ['e', 'e'],
    "orange" : ['e', 'ne']}
SETTING_LIST = [''] + list(PIECES_GENERATOR.keys())
LOCAL_MOVE_LIST = ['r', 'r', 'r', 'r', 'r','r']
ICON_PATH = './images/Star_icon_stylized.svg.png'
ABOUT=[
    'Star Puzzle',
    'Programmed by Pierre Lanquetot',
    'September-October 2023',
    'Use buttons in upper menu to set, solve, etc.',
    'Have fun!']

################################################################################
#                           CLASSES                                            #
################################################################################

class GridPoint(puzzles.hex_game.GridPoint):
        
    def __init__(self,
                 Hx=0, 
                 Hy=0, 
                 Hz=0, 
                 x_offset= 0, 
                 y_offset = 0, 
                 setting_list = [''], 
                 radius = 10):
        
        super().__init__(
                 Hx=Hx, 
                 Hy=Hy, 
                 Hz=Hz, 
                 x_offset=x_offset, 
                 y_offset =y_offset, 
                 setting_list =setting_list, 
                 radius = radius)
        
        
    def display_update(self):
        self.image.fill((255,255,255,0))
        if self.setting != '':		
            self.image = pygame.image.load("./images/star_" + self.setting + ".png")
            pygame.draw.circle(
                self.image,
                (0,0,0,255),
                (25,25),
                self.radius)
            self.rect = self.image.get_rect()
            self.update_2D()
            self.image.set_alpha(128)
        else:
            super().display_update()    
            
    
class PieceElement(puzzles.hex_game.PieceElement):
    
    image: pygame.Surface
    rect: pygame.Rect
    
    def __init__(self,
                 colour,
                 Hx = 0,
                 Hy = 0,
                 Hz = 0,
                 x_offset = 0,
                 y_offset = 0):
        
        super().__init__(colour,
                         Hx=Hx,
                         Hy=Hy,
                         Hz=Hz,
                         x_offset=x_offset,
                         y_offset=y_offset)
        
        # Create a surface for the sprite - a bubble image
        self.image = pygame.image.load("./images/star_" + colour + ".png")

        # Set the sprite's rect (position and size)
        self.rect = self.image.get_rect()

class Piece(puzzles.hex_game.Piece):
    
    origin: PieceElement
    
    def __init__(self, setting, 
              deck_position_x = 0, 
              deck_position_y = 0, 
              piece_build_sequence = [],
              local_move_list = LOCAL_MOVE_LIST):
        
        super().__init__(
            setting,
            deck_position_x,
            deck_position_y,piece_build_sequence=piece_build_sequence,
            local_move_list = local_move_list)

        # Add first element to the group
        piece_element_1 = PieceElement(
            setting,
            x_offset = deck_position_x,
            y_offset = deck_position_y)
        
        self.add(piece_element_1)
        self.origin = piece_element_1

        # create elements based on build_sequence of moves
        ref_elt = piece_element_1
        for move in piece_build_sequence:
            new_element = PieceElement(
                ref_elt.setting,
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
    
class Grid(puzzles.hex_game.Grid):

    def __init__(self,
                 width=0,
                 height=0,
                 x_offset = 0,
                 y_offset = 0,
                 setting_list = [''],
                 point_list = []):
        
        super().__init__(
            width,
            height,
            x_offset,
            y_offset,
            setting_list,
            point_list)

        for Y in range(height):
            P = GridPoint(
                x_offset = x_offset,
                y_offset = y_offset,
                setting_list = setting_list) #initiate point at origin

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
    
################################################################################
#                    BUILDING FUNCTIONS                                        #
################################################################################

def create_star_image(piece):
    # Read the elementary star Image
    # colour is a string
    image = tkinter.Image.open("./images/6_star_original_turned.png") # type: ignore

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

class StarGame(puzzles.hex_game.HexGame):

    grid: Grid

    def __init__(self, screen):
        
        super().__init__(
            screen,
            icon_path=ICON_PATH,
            about_text=ABOUT,
            name='StarGame',
            caption='Star Game',
            setting_list=SETTING_LIST,
            pieces_generator=PIECES_GENERATOR
        )

    def build_grid(self):
        
        self.grid = Grid(
            GRID_WIDTH,
            GRID_HEIGHT,
            0,
            0,
            SETTING_LIST)
        self.grid.compute_rect()

    def build_pieces(self):
        super().build_pieces(piece_class=Piece)