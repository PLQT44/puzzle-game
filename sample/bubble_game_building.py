# src/puzzles/star_game.py

# Marie-Aimee's bubble puzzle
# it is a subclass of HexGame
# it needs multi-piece on a grid point 

# imports
from cmath import pi, tau
import os
import pygame

################################################################################
#                          CONSTANTS                                           #
################################################################################

PIECES_GENERATOR = { 'yellow' : [['out', 'w', 'e'], ['out', '', 'ne'], ['out', 'nw', '']],
                    'light_green' : [['in', 'e', 'e'], ['out', '', 'e'], ['out', 'nw', '']],
                    'purple' : [['out', 'se', 'e'], ['out', '', 'ne'], ['in', 'sw', '']], 
                    'fuchsia' : [['in', 'e','e'], ['out', 'sw', 'ne'], ['in', 'sw', '']],
                    'blue' : [['in', 'e', 'e'], ['in', 'nw,w', 'nw'], ['out', 'w', '']],
                    'light_blue' : [['out', 'nw', 'e'], ['out', '', 'ne'], ['in', 'sw', '']],
                    'violet' : [['in', 'e', 'e'], ['out', 'nw,ne', 'e'], ['in', 'w', '']],
                    'green' : [['in', 'e', 'e'], ['in', 'nw,w', 'nw'], ['out', 'nw', '']],
                    'lagoon' : [['in', 'e', 'e'], ['out', '', 'e'], ['out', 'ne', '']],
                    'pink' : [['in', 'e', 'e'], ['out', '', 'ne'], ['out', 'w', '']],
                    'orange' : [['in', 'e', 'e'], ['out', 'e', 'nw'], ['in', 'se', '']],
                    'red' : [['in', 'e', 'e'], ['out','se', 'nw'], ['out', 'e', '']]
                    }

COLOURS = { 'black' : (0,0,0,255),
            'yellow' : (255, 255, 0, 255), 
            'light_green' : (124,252,0,255),
            'purple' : (128,0,128, 255),
            'fuchsia' : (255,20,147,255),
            'blue' :(0,0,128,255),
            'light_blue' :(0,191,255,255),
            'violet' : (186,85,211,255),
            'green' : (0,128,0,255),
            'lagoon' :(64,224,208,255),
            'pink' : (255,105,180,255),
            'orange' : (255,140,0,255),
            'red' :(255,0,0,255)
            }

OUT_ANGLE_DICT = {'' : (0, tau),
                  'w' : (7*pi/6, 5*pi/6),
                  'nw' : (5*pi/6, pi/2),
                  'se' : (11*pi/6, 3*pi/2),
                  'sw' : (3*pi/2, 7*pi/6),
                  'nw,ne' : (5*pi/6, pi/6),
                  'ne' : (pi/2, pi/6),
                  'e' : (pi/6, 11*pi/6)
                  }

IN_ANGLE_DICT = {'e' : 0,
                 'ne' : 60,
                 'nw' : 120,
                 'w' : 180,
                 'sw' : 240,
                 'se' : 300}

LOCAL_MOVE_LIST = ['r', 'r', 'r', 'r', 'r','r,f', 'r', 'r','r', 'r','r','r,f']

# ICON_PATH = './images/Star_icon_stylized.svg.png'

################################################################################
#                    BUILDING FUNCTIONS                                        #
################################################################################

def create_out_bubble(name, setting = ['out', '', '']): #THIS IS GOING TO BE A FUNNY ONE!!!

    image = pygame.Surface((50, 50), pygame.SRCALPHA)
    image.set_colorkey((0, 0, 0, 0))
    image.fill((255, 255, 255, 0))	 # Fill with transparent white
    rect = image.get_rect()

    start_angle, stop_angle = OUT_ANGLE_DICT[setting[1]]

    pygame.draw.arc(image, COLOURS[name], rect, start_angle,stop_angle, 10)

    return image

def double_branch(surface, name, setting_string):
    setting_list = setting_string.split(',')

    image = pygame.transform.rotozoom(surface, 60, 1) #there is always 60 degrees difference when there are two branches
    rect = image.get_rect()
    
    inside_rect = pygame.Rect(rect.centerx, rect.centery - 7, 30, 14)
    pygame.draw.rect(image, COLOURS[name], inside_rect)

    image = pygame.transform.rotozoom(image, IN_ANGLE_DICT[setting_list[0]], 1) #set less rotated branch in direction
    
    return image

def create_in_bubble(name, setting):
    image = pygame.Surface((50, 50), pygame.SRCALPHA)
    image.fill((255, 255, 255, 0))	 # Fill with transparent white
    rect = image.get_rect()
    center_point = rect.center

    pygame.draw.circle(image, COLOURS[name], center_point, 14)

    inside_rect = pygame.Rect(rect.centerx, rect.centery - 7, 25, 14)

    pygame.draw.rect(image, COLOURS[name], inside_rect)

    if ',' not in setting[1]:
        image = pygame.transform.rotozoom(image, IN_ANGLE_DICT[setting[1]],1)
    else:
        image = double_branch(image, name, setting[1])

    rect = image.get_rect(center = center_point, width = 50, height = 50)

    result_image = pygame.Surface((50,50), pygame.SRCALPHA)
    result_image.blit(image, rect)

    return result_image

def create_bubble_image(name = 'black', setting = ['in', '', '']): #THIS IS GOING TO BE A FUNNY ONE!!!
    
    if setting[0] == 'out':
        image = create_out_bubble(name, setting)
    elif setting[0] == 'in':
        image = create_in_bubble(name, setting)
    else:
        raise Exception("I don't know that kind of bubble")

    file_name = f"./images/bubble_{name}_{setting[0]}_{setting[1]}.png"

    # Create the directory if it doesn't exist
    directory = os.path.dirname(file_name)
    if not os.path.exists(directory):
        os.makedirs(directory)

    pygame.image.save(image, file_name)

for name, setting_list in PIECES_GENERATOR.items():
    for setting in setting_list:
        create_bubble_image(name, setting)