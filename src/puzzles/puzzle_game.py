# puzzle_game.py

# this is where I define the generic puzzle game
# it has a grid made of points, pieces
# it can start, solve

# imports
from itertools import cycle
import random
import pygame
from constants import RGB_COLOURS
import exceptions as exc


################################################################################
#                           PUZZLE'S CLASSES                                   #
################################################################################

class GamePoint(pygame.sprite.Sprite):
    # It is basically a sprite

    def __init__(self, x_offset=0, y_offset=0):
        super().__init__()
        self.image = pygame.Surface((1, 1))

        # offset values correspond to the x,y location of the origin point
        self.x_offset = x_offset
        self.y_offset = y_offset

        # Set the sprite's rect (position and size)
        self.rect = self.image.get_rect()
        
    def translate(self, vector):
        pass

    def rotate(self, rotation_center):
        pass

    def distance(self, point):
        pass

    def neighbouring(self, point):
        pass

    def update(self):
        pass

    def clone(self):
        return GamePoint(self.x_offset, self.y_offset)

class GridPoint(GamePoint):
    # this is a point for a grid.
    # It has a number of specific properties
    # it has a setting that is basically set to '' but can browse throuh an iterator
    # a reference to the occupying piece (or pieces --> I use a list)

    def __init__(self, x_offset, y_offset, setting_list):
        super().__init__(x_offset, y_offset)

        # what can be the setting value
        self.setting_pool = cycle(setting_list)

        #   piece and element reference
        self.setting_list = setting_list
        self.setting = next(self.setting_pool)
        self.pieces = []
        self.elements = []

    def is_free(self):
        return len(self.elements) < 2

    def display_update(self):
        pass

    def update(self, event_list=[]):
        super().update()

        for event in event_list:
            # handle setting logic
            if event.type == pygame.MOUSEBUTTONDOWN:
                if (event.button == 4
                        and self.rect.collidepoint(event.pos)
                        and self.status in ['base', 'set']):  # roulet scroll up mouse over the point
                    self.setting = next(self.setting_pool)

        self.image.fill((255, 255, 255, 0))
        self.display_update()

    def clone(self):
        return GridPoint(self.x_offset, self.y_offset, self.setting_list)

    def reinit(self):
        self.status = 'base'
        self.setting = ''
        self.pieces = []
        self.elements = []

class PieceElement(GamePoint):
    # this is the basic constituent of a piece
    # it has a colour
    # it has a status indicator indicating where the piece is:
    #  'base', 'moving', 'attracted, 'installed'
    # it has a reference to its attachment grid_point when installed

    def __init__(self, setting, x_offset=0, y_offset=0):
        super().__init__(x_offset, y_offset)

        # Create a surface for the sprite - a star image
        # Set the sprite's rect (position and size)

        self.setting = setting
        self.status = 'base'
        self.grid_point = None

    def update(self):
        super().update()

    def flip(self):
        pass

    def clone(self):
        return PieceElement(self.setting, self.x_offset, self.y_offset)

class Piece(pygame.sprite.Group):

    # a piece is a subclass of group that groups several piece_elements
    # a Piece has a setting, an origin element
    # it has a "unit_move" index

    def __init__(self, setting, deck_position_x=0, deck_position_y=0, piece_build_sequence = [], local_move_list = []):
        super().__init__()

        self.setting = setting
        self.status = 'base'
        self.deck_position_x = deck_position_x
        self.deck_position_y = deck_position_y
        self.build_sequence = piece_build_sequence
        self.local_move_list = local_move_list
        self.local_move_length = len(local_move_list)
        self.local_move_index = 0
        self.bounding_rect = pygame.Rect(0,0,0,0)        
    
    def translate(self, vector):
        # translates all piece elements by vector
        for element in self.sprites():
            element.translate(vector)

    def set_2D(self, x, y):
        self.deck_position_x = x
        self.deck_position_y = y
        for element in self.sprites():
            element.set_2D(x,y)
        self.compute_rect()

    def compute_rect(self):
        sprites = self.sprites()
        min_x = min([sprite.rect.x for sprite in sprites])
        min_y = min([sprite.rect.y for sprite in sprites])
        max_x = max([sprite.rect.right for sprite in sprites])
        max_y = max([sprite.rect.bottom for sprite in sprites])
        self.bounding_rect.topleft = (min_x, min_y)
        self.bounding_rect.size = (max_x-min_x, max_y-min_y)

    def reinit(self):
        pass

    def reinit_to_deck(self):
        self.reinit()

        for element in self.sprites():
            element.x_offset = self.deck_position_x
            element.y_offset = self.deck_position_y
            if not (element.grid_point is None):
                element.grid_point.pieces = []
                element.grid_point.elements = []
            element.grid_point = None
            element.status = 'base'

        self.status = 'base'

    def set_pos(self, point):
        pass

    def next_move(self, point_index, free_grid):
        if self.local_move_index < self.local_move_length - 1:
            self.next_local_move()
            return point_index
        #I have already made all local moves
        self.reinit_to_deck() #back to basic location
        point_index += 1
        try: #try next point in free_grid
            current_point = free_grid[point_index]
            self.set_pos(current_point)
            return point_index 
        except: #I tried all free points
            raise exc.FinalMove

    def local_unit_move(self, local_move = ''):
        self.local_move_index += 1
        self.local_move_index = self.local_move_index % self.local_move_length

    def next_local_move(self):
        self.local_unit_move(self.local_move_list[self.local_move_index])

    def attach(self, elements_dict):
        self.status = 'installed'
        self.set_pos(elements_dict[self.origin])

        for element in self.sprites():
            element.status = 'installed'
            element.grid_point = elements_dict[element]
            element.grid_point.status = 'installed'
            if element not in element.grid_point.elements:
                element.grid_point.elements.append(element)
            if self not in element.grid_point.pieces:
                element.grid_point.pieces.append(self)
            
    def detach(self, target_status):
        # this function removes the piece from a grid.
        # the target status depends if I am handling movement (in which case it is 'attracted') or solving puzzle (in which case it is 'base')

        for element in self.sprites():
            if target_status == 'base':
                element.grid_point.pieces.remove(self)
                element.grid_point.elements.remove(element)
                element.grid_point = None
            element.status = target_status
            element.x_offset = self.origin.rect.centerx
            element.y_offset = self.origin.rect.centery

        # manage status
        self.status = target_status

    def matching_points(self, grid):
        # just returns the dictionary of matching points which are not installed; keys are PieceElements, values are GridPoints 

        # let's test and handle collisions!
        collide_dict = pygame.sprite.groupcollide(
            self, grid, False, False, pygame.sprite.collide_rect_ratio(0.1))

        # remove occupied points
        proper_dict = {}
        for element, point_list in collide_dict.items():
            for point in point_list:
                if ((point.status in ['base', 'attracted'] and point.setting == '') or (point.setting == element.setting)):
                    proper_dict[element] = point
                break

        return proper_dict

    def check_fit(self, grid):
        # test collision with the grid, returns a dictionary of attachment points and a success boolean
        points_dict = self.matching_points(grid)
        set_points = grid.set_points(self.setting)

        # if some grid points' setting is set, check if all these points are matching
        if all((point in points_dict.values()) for point in set_points):
            # let's check if the whole piece fits in
            return all((element in points_dict.keys()) for element in self.sprites()), points_dict
        else:
            return False, points_dict

    def status_update(self, match, match_dict, grid):
        if match:
            self.status = 'attracted'
            for element in self.sprites():
                element.status = 'attracted'
                element.grid_point = match_dict[element]
                if not element in element.grid_point.elements:
                    element.grid_point.elements.append(element)
                if not self in element.grid_point.pieces:
                    element.grid_point.pieces.append(self)
                   
        elif self.status == 'attracted':  # i was attracted but that's not the case anymore
            self.status = 'moving'
            for element in self.sprites():
                element.status = 'moving'
                element.grid_point.pieces.remove(self)
                element.grid_point.elements.remove(element)
                element.grid_point = None
            
        grid.normalize(self,match_dict)

    def update(self, grid, event_list = []):
        # I override the update() method here, to handle at piece level all the moving logics
        super().update()

        for event in event_list:
            # Handle group-level dragging logic
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # left mouse button is pressed
                    # mouse button is over a sprite in the piece and this is the piece I want to select
                    if self.is_clicked_piece(event):
                        if self.status == 'base':  # the piece was in the deck, now it moves
                            # I register the relative position of mouse and of origin piece
                            self.origin.offset_x = self.origin.rect.centerx - \
                                event.pos[0]
                            self.origin.offset_y = self.origin.rect.centery - \
                                event.pos[1]
                            self.status = 'moving'
                            for element in self.sprites():
                                element.status = 'moving'

                        elif self.status == 'installed':  # the piece was installed, i detach it
                            # I register the relative position of mouse and of origin piece
                            self.origin.offset_x = self.origin.rect.centerx - \
                                event.pos[0]
                            self.origin.offset_y = self.origin.rect.centery - \
                                event.pos[1]
                            self.detach('attracted')

                elif event.button == 3:  # right button pressed
                    if self.status == 'attracted':
                        for element in self.sprites():
                            element.grid_point.pieces.remove(self)
                            element.grid_point.elements.remove(element)
                            element.grid_point = None
                        self.status = 'moving'
                    if self.status in ['moving', 'attracted']:
                        self.next_local_move()
                        # update the matching status
                        match, match_dict = self.check_fit(grid)
                        self.status_update(match, match_dict, grid)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if self.status == 'moving':
                        self.reinit_to_deck()

                    elif self.status == 'attracted':
                        match, match_dict = self.check_fit(grid)
                        self.attach(match_dict)

            elif event.type == pygame.MOUSEMOTION:
                if self.status in ['moving', 'attracted']:  # actually dragging
                    new_origin_x = pygame.mouse.get_pos()[
                        0] + self.origin.offset_x
                    new_origin_y = pygame.mouse.get_pos()[
                        1] + self.origin.offset_y
                    for element in self.sprites():  # all elements move like origin
                        element.x_offset = new_origin_x
                        element.y_offset = new_origin_y
                        element.update_2D()

                    # update matching status
                    match, match_dict = self.check_fit(grid)
                    self.status_update(match, match_dict, grid)

    def is_clicked_piece(self, event):
        return any(sprite.rect.collidepoint(event.pos) for sprite in self.sprites())

class Grid(pygame.sprite.Group):
    # Grid is a group of GridPoint
    # it has a grid offset for showing on the 2D screen, which is th x and y of the origin point

    def __init__(self, width=0, height=0, x_offset=0, y_offset=0, point_list=[]):
        super().__init__()
        # Each grid has a height and a width (X axis)
        self.width = width
        self.height = height
        self.x_offset = x_offset
        self.y_offset = y_offset

        self.add(point_list)
        self.bounding_rect = pygame.Rect(0,0,0,0)

    def set_points(self, setting=''):
        if setting == '':
            return []
        else:
            return [point for point in self.sprites() if point.setting == setting]

    def normalize(self, piece, attracted_points):
        # attracted_points is a dictionary of piece elements with attracted point
        # browse through the points and remove piece and element from point's lists, if needed
        for grid_point in self.sprites():
            if (not (grid_point in attracted_points.values())) and (piece in grid_point.pieces) :
                grid_point.pieces.remove(piece)
                for element in piece:
                    if element in grid_point.elements:
                        grid_point.elements.remove(element)

    def free_points(self):
        # returns a list of free points
        return [point for point in self.sprites() if point.is_free()]
    
    def compute_rect(self):
        sprites = self.sprites()
        min_x = min([sprite.rect.x for sprite in sprites])
        min_y = min([sprite.rect.y for sprite in sprites])
        max_x = max([sprite.rect.right for sprite in sprites])
        max_y = max([sprite.rect.bottom for sprite in sprites])
        self.bounding_rect.topleft = (min_x, min_y)
        self.bounding_rect.size = (max_x-min_x, max_y-min_y)

    def reinit(self):
        for point in self.sprites():
            for piece in point.pieces:
                piece.reinit_to_deck()
            point.reinit()

###############################################################################
#                   THE GLOBAL CLASS                                          #
###############################################################################

class PuzzleGame():

    def __init__(self, name, caption, icon_path, setting_list = [''], pieces_generator = {}):
        self.name = name
        self.complete_game = True
        self.icon = pygame.image.load(icon_path)
        self.caption = caption
        self.setting_list = setting_list
        self.pieces_generator = pieces_generator

    def start(self, screen_width, screen_height, reference_message):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.build_grid()
        self.build_pieces(self.pieces_generator)
        self.start_layout(reference_message, main_label_padding=50)

    def start_layout(self, reference_message, main_label_padding):
        #create font
        self.game_font = pygame.font.Font(None, 36)
        
        #initiate main label's message
        self.main_message = reference_message

        #create Sprite for the main label text
        self.main_label_padding = main_label_padding
        self.main_text_surface = self.game_font.render(self.main_message, True, RGB_COLOURS['black'])  # Text, antialiasing, color
        self.main_label = pygame.sprite.Sprite()
        self.main_label.image = self.main_text_surface
        self.main_label.rect = self.main_text_surface.get_rect(x=(self.screen_width-self.main_text_surface.get_width())/2,
                                                               y = self.main_label_padding)
        
        #Store the label's height
        self.main_label_height = self.main_label.image.get_height() + 2*self.main_label_padding

        #create rectangle sprite to show around main label
        self.main_label_frame = pygame.sprite.Sprite()
        self.main_label_frame.image = pygame.Surface((self.screen_width, self.main_label_height))
        self.main_label_frame.image.fill('white')
        self.main_label_frame.rect = self.main_label_frame.image.get_rect()
        pygame.draw.rect(self.main_label_frame.image, (0,0,0), 
                         self.main_label_frame.rect, width=2, border_radius=20)

        #create rectangle sprite to show around the grid
        self.grid_frame = pygame.sprite.Sprite()
        self.grid_frame.image = pygame.Surface((self.screen_width, 0.7*(self.screen_height - self.main_label_height)))
        self.grid_frame.image.fill('white')
        self.grid_frame.rect = self.grid_frame.image.get_rect()
        self.grid_frame.rect.topleft = (0, self.main_label_height)
        pygame.draw.rect(self.grid_frame.image, (0,0,0), 
                         self.grid_frame.image.get_rect(), width=2, border_radius=20)

        #create rectangle sprite to show around the deck
        self.deck_frame = pygame.sprite.Sprite()
        self.deck_frame.image = pygame.Surface((self.screen_width, 0.3*(self.screen_height - self.main_label_height)))
        self.deck_frame.image.fill('white')
        self.deck_frame.rect = self.deck_frame.image.get_rect()
        self.deck_frame.rect.bottomleft = (0, self.screen_height)
        pygame.draw.rect(self.deck_frame.image, (0,0,0), 
                         self.deck_frame.image.get_rect(), width=2, border_radius=20)


        #create group for theses layout sprites, and add the sprites
        self.layout_sprites = pygame.sprite.Group()
        self.layout_sprites.add(self.main_label_frame)
        self.layout_sprites.add(self.grid_frame)
        self.layout_sprites.add(self.deck_frame)
        self.layout_sprites.add(self.main_label)

        #finally, position grid and deck correctly
        self.layout_update()

    def update_main_label(self, message):
        #mask previous text
        self.main_label.image.fill("white")
    
        #show new text
        self.main_label.image = self.game_font.render(message, True, RGB_COLOURS['black'])  # Text, antialiasing, color
        self.main_label.rect.topleft = ((self.screen_width-self.main_label.image.get_width())/2
                                       , self.main_label_padding)

    def solve(self, surface):
        self.build_deck(self.pieces_dict)
        # random.shuffle(self.deck)
        self.recursive_pose(surface)
    
    def reinit(self):
        self.grid.reinit()
        for piece in self.pieces_dict.values():
            piece.reinit_to_deck()
    
    def layout_update(self):
        self.position_grid(0, self.main_label_height
                           , self.screen_width, 0.7*(self.screen_height - self.main_label_height))
        self.piece_distribute(0.3*(self.screen_height - self.main_label_height))

    def draw(self, event_list, surface):
        
        for piece in self.pieces_dict.values():
            piece.update(self.grid, event_list) #moving and rotating pieces, checking for collisions
        self.grid.update(event_list)

        #show the sprites
        self.layout_sprites.draw(surface)
        self.grid.draw(surface)
        self.pieces_group.draw(surface)
        
        # self.draw_rects(surface)

    def draw_rects(self, surface):
        pygame.draw.rect(surface, (255,0,0,255), self.grid.bounding_rect, 2)
        for element in self.pieces_group.sprites():
            pygame.draw.rect(surface, (255, 0, 0, 255), element.rect, 2)
        for element in self.grid.sprites():
            pygame.draw.rect(surface, (0, 0, 255, 255), element.rect, 1)
        for piece in self.pieces_dict.values():
            pygame.draw.rect(surface, (0, 255, 0, 255), piece.bounding_rect, 1)

    def build_grid(self):
        self.grid = Grid() #create a new grid

    def build_pieces(self, generator, piece_class = Piece):
        # generate pieces. I put pieces in a sprites group, and also in a dictionary for easier browsing
        #WARNING ALL PIECES ARE IN 0 POSITION IN THIS REFERENCE METHOD, NEED TO DISTRIBUTE
        self.pieces_group = pygame.sprite.Group()
        self.pieces_dict = {}

        for setting, piece_build_sequence in generator.items():
            new_piece = piece_class(colour=setting, piece_build_sequence=piece_build_sequence)
            self.pieces_group.add(new_piece)
            self.pieces_dict[setting] = new_piece
    
    def position_grid(self, x, y, width, height):
        self.grid.compute_rect()
        x_padding = x + ((width - self.grid.bounding_rect.width)/2) + (self.grid.x_offset - self.grid.bounding_rect.left) 
        y_padding = (y
                    + (height - self.grid.bounding_rect.height)/2
                    + self.grid.bounding_rect.height
                    + (self.grid.y_offset - self.grid.bounding_rect.bottom))

        self.grid.x_offset = x_padding
        self.grid.y_offset = y_padding

        for point in self.grid.sprites():
            point.x_offset = x_padding
            point.y_offset = y_padding
            point.update_2D()

        self.grid.compute_rect()

    def piece_distribute(self, height):
        num_pieces = len(self.pieces_dict.keys())
        
        cumulated_pieces_width = sum([piece.bounding_rect.width for piece in self.pieces_dict.values()])
        x_deck_spacing = (self.screen_width - cumulated_pieces_width)/(num_pieces + 1)

        y_padding = (height-max([piece.bounding_rect.height for piece in self.pieces_dict.values()]))/2

        reference_y = self.screen_height - y_padding
        reference_x = x_deck_spacing

        for piece in self.pieces_dict.values():
            piece.set_2D(reference_x + piece.origin.rect.centerx - piece.bounding_rect.left, 
                         reference_y + piece.origin.rect.centery - piece.bounding_rect.bottom)
            reference_x += piece.bounding_rect.width + x_deck_spacing

    def build_deck(self, pieces_dict):
        # takes the current status of the grid and of the pieces_dictionary, and returns a list of pieces which are still not installed, for solving algorithm
        # pieces_dict is structured as {piece_name : piece}
        self.deck = [piece for piece in pieces_dict.values() if piece.status == 'base']

    ###############################################################################
    #                       SOLVING FUNCTIONS                                     #
    ###############################################################################

    def recursive_pose(self, surface):

        # the core of the solving program. Tries to fill the grid with pieces in the deck. Returns the new grid and deck or exc.SolvingImpossibility if no solution is found
        self.show(surface)

        # free_points() should return an optimised list of free points
        # including split, sort, elimination of two small sub-grids, sorting based on setting
        free_grid = self.grid.free_points()

        if len(free_grid) == 0 or len(self.deck) == 0:  # no more free points or placed all pieces, cool!
            return

        # I have free points, let's continue
        # Put the pieces that have points with their colours set at beginning
        # set_settings_list = [point.setting for point in self.grid.sprites() if point.setting != '']
        # self.deck.sort(key=lambda piece: piece.setting in set_settings_list, reverse=True)

        # let's analyse the split grid and optimise accordingly
        grid_list = self.grid_split(free_grid)
        sorted_grid_list = sorted(grid_list, key=lambda grid: len(grid))  # sort it

        if self.complete_game and len(sorted_grid_list[0]) < min([len(piece.sprites()) for piece in self.deck]):
            # it is a "complete" game (all points must be occupied) 
            # and the smallest sub-grid is smaller than the desk minimum
            raise exc.SolvingImpossibility
            
        while len(sorted_grid_list[0]) < min([len(piece.sprites()) for piece in self.deck]):
            #I can just remove the points of the sub_grid from the free grid
            for point in sorted_grid_list[0]:
                free_grid.remove(point)
            sorted_grid_list.pop(0)
            if len(sorted_grid_list) == 0:
                break                
        
        if len(free_grid) == 0 and len(self.deck) >0:
            raise exc.SolvingImpossibility

        # shuffle the free_grid
        random.shuffle(free_grid)

        point_index = 0
        current_point = free_grid[point_index]  # let's start with first free point
        piece_index = 0
        current_piece = self.deck[piece_index]  # take the first piece in the deck
        current_piece.set_pos(current_point)  # I place in first grid's free point

        # now is the main loop
        while_exit = False
        while not (while_exit):
            # try to put the current_piece on the grid
            success, fitting_points = current_piece.check_fit(self.grid)
            if success:  # it fits!
                current_piece.attach(fitting_points)
                self.deck.pop(piece_index)
                # now let's enter next recursion level
                try:
                    self.recursive_pose(surface)
                    return
                except exc.SolvingImpossibility:  # I didn't manage to solve the sub-grid
                    current_piece.detach('base')
                    # logically put the piece back in the deck
                    self.deck.insert(piece_index, current_piece)
                    # I need to make the next move for piece
                    try:
                        point_index = current_piece.next_move(point_index, free_grid)
                    except exc.FinalMove:
                        while_exit = True

            else:  # if piece does not fit, I move to next possibility
                try:
                    point_index = current_piece.next_move(point_index, free_grid)
                except exc.FinalMove:
                    while_exit = True
        
        raise exc.SolvingImpossibility

    def group_distance(anchor_point, point_list):
        if len(point_list) > 0:
            return min([anchor_point.distance(point) for point in point_list])
        else:
            return 0

    def find_neighbour(self, anchor_point, point_list):
        # I browse through the points of the grid to see if one is neighboring the given point
        for point in point_list:
            if point.neighbouring(anchor_point):
                return point

        raise exc.NoNeighbour

    def grid_split(self, target_list, anchor_list=None):
        # separates a list of free points in a list of independent list of free points
        # anchor_list is an list containing points from which I try to expand in grid

        if len(target_list) == 0:  # no free point, answer is the origin grid
            if anchor_list is None:
                return []
            return [anchor_list]

        else:  # there are at least 1 free point in target_grid, I can evaluate neighbouring and start recursion
            result_list = [] + target_list

            if anchor_list is None:  # create the initial point to grow from
                anchor_list = [result_list[0]]

            for anchor_point in anchor_list:
                # anchor point is outside of grid
                if anchor_point in result_list:
                    result_list.remove(anchor_point)
                try:  # let's try to find a neighbour to the anchor point
                    neighbour = self.find_neighbour(anchor_point, result_list)
                    # if I find a neighbour, I start recursing, anchoring in that neighbour
                    anchor_list.append(neighbour)
                    result_list.remove(neighbour)
                    result = self.grid_split(result_list, anchor_list)
                    return result

                except exc.NoNeighbour:  
                    # anchor_point has no neighbour --> I will check with another
                    # point in anchor_grid. If all anchor points have been tried,
                    # it means I have an independant grid
                    pass

            result = [anchor_list] + self.grid_split(result_list)
            return result
