# puzzle_game.py

# this is where I define the generic puzzle game
# it has a grid made of points, pieces
# it can start, solve

# imports
from itertools import cycle
from math import ceil
import random
from typing import Iterator
import pygame
import pygame_menu
from constants import RGB_COLOURS
import exceptions as exc

ABOUT = ['Author : Pierre LANQUETOT',
          'This is the generic Puzzle Game',
          'You should not really play it']

MY_THEME = pygame_menu.themes.Theme()

MY_THEME.background_color = 'grey10'
MY_THEME.border_color = 'grey50'
MY_THEME.border_width=0
MY_THEME.surface_clear_color='white'

MY_THEME.cursor_color = 'black'
MY_THEME.cursor_selection_color=(70,70,70,100)
MY_THEME.cursor_switch_ms=500

MY_THEME.fps=60

MY_THEME.readonly_color='deepskyblue4'
MY_THEME.readonly_selected_color='darkblue'

MY_THEME.scrollarea_outer_margin=(0,0)

MY_THEME.scrollbar_color='grey20'
MY_THEME.scrollbar_cursor= pygame.SYSTEM_CURSOR_HAND
MY_THEME.scrollbar_shadow= True
MY_THEME.scrollbar_shadow_color='honeydew4'
MY_THEME.scrollbar_shadow_offset= 2
MY_THEME.scrollbar_shadow_position=pygame_menu.locals.POSITION_SOUTHWEST
MY_THEME.scrollbar_slider_color='grey30'
MY_THEME.scrollbar_slider_hover_color= 'grey15'
MY_THEME.scrollbar_slider_pad= 0
MY_THEME.scrollbar_thick= 20

MY_THEME.title=True
MY_THEME.title_background_color='grey70'
MY_THEME.title_bar_modify_scrollarea=True
MY_THEME.title_bar_style= pygame_menu.widgets.MENUBAR_STYLE_SIMPLE
MY_THEME.title_close_button=True
MY_THEME.title_close_button_background_color= 'black'
MY_THEME.title_close_button_cursor= pygame.SYSTEM_CURSOR_HAND
MY_THEME.title_fixed= True
MY_THEME.title_float=False
MY_THEME.title_font= pygame_menu.font.FONT_MUNRO
MY_THEME.title_font_antialias= True
MY_THEME.title_font_color= 'white'
MY_THEME.title_font_shadow=True
MY_THEME.title_font_shadow_color='paleturquoise4'
MY_THEME.title_font_shadow_offset=3
MY_THEME.title_font_shadow_position= pygame_menu.locals.POSITION_SOUTHWEST
MY_THEME.title_font_size= 70
MY_THEME.title_offset= (10,5)
MY_THEME.title_updates_pygame_display= True

MY_THEME.widget_box_arrow_margin=(5,5,5)
MY_THEME.widget_box_arrow_color = 'deepskyblue4'
MY_THEME.widget_box_background_color = 'slategrey'
MY_THEME.widget_box_border_color = 'slategray1'
# MY_THEME.widget_box_border_width=3
# MY_THEME.widget_box_inflate =(20,20)
# MY_THEME.widget_box_margin = (5,5)

MY_THEME.widget_cursor = pygame.SYSTEM_CURSOR_HAND

MY_THEME.widget_alignment= pygame_menu.locals.ALIGN_CENTER
MY_THEME.widget_alignment_ignore_scrollbar_thickness= False
# MY_THEME.widget_background_color=(240,200,48)
# MY_THEME.widget_background_inflate = (50,50)
# MY_THEME.widget_background_inflate_to_selection=True
MY_THEME.widget_border_color ='grey95'
MY_THEME.widget_border_width = 0

MY_THEME.selection_color='whitesmoke'
MY_THEME.widget_font = pygame_menu.font.FONT_MUNRO
MY_THEME.widget_font_antialias = True
MY_THEME.widget_font_background_color = None
MY_THEME.widget_font_background_color_from_menu = False
MY_THEME.widget_font_color = 'grey70'
MY_THEME.widget_font_shadow = True
MY_THEME.widget_font_shadow_color = 'deepskyblue4'
MY_THEME.widget_font_shadow_offset = 2
MY_THEME.widget_font_shadow_position = 'position-southwest'
MY_THEME.widget_font_size = 50

MY_THEME.widget_margin = (0,15)
# MY_THEME.widget_padding (int, float, tuple, list) – Padding of the widget according to CSS rules. It can be a single digit, or a tuple of 2, 3, or 4 elements. Padding modifies widget width/height
MY_THEME.widget_offset = (0,15)

MY_THEME.widget_selection_effect = pygame_menu.widgets.SimpleSelection()

MY_THEME.widget_shadow_aa = 2
MY_THEME.widget_shadow_color = 'midnightblue'
MY_THEME.widget_shadow_radius =15
MY_THEME.widget_shadow_type = 'rectangular'
MY_THEME.widget_shadow_width = 0
MY_THEME.widget_tab_size = 50

class Label_Timer():

    def __init__(self, state = False, duration = 1000):
        self.state =  state
        self.duration = duration

    def start(self, start_time):
        self.start_time = start_time
        self.state = True

        return self.state

    def update_state(self, current_time):
        if self.state == True and current_time-self.start_time < self.duration:
            self.state = True
        else:
            self.state = False

        return self.state


################################################################################
#                           PUZZLE'S CLASSES                                   #
################################################################################

class GamePoint(pygame.sprite.Sprite):
    # It is basically a sprite
    
    x_offset: int
    y_offset: int
    image: pygame.Surface
    rect: pygame.Rect
    
    def __init__(self, x_offset=0, y_offset=0):
        super().__init__()

        # offset values correspond to the x,y location of the origin point
        self.x_offset = x_offset
        self.y_offset = y_offset

        # Set the sprite's image and rect (position and size)
        self.image = pygame.Surface((1, 1))
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

    setting_list: list
    setting_pool: Iterator
    setting: str
    pieces: list
    elements: list

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
        return len(self.elements) == 0

    def display_update(self):
        pass

    def update(self, event_list):
        super().update()

        for event in event_list:
            # handle setting logic
            if event.type == pygame.MOUSEBUTTONUP:
                if (event.button == 4
                        and self.rect.collidepoint(event.pos)
                        and len(self.elements) == 0):  # roulet scroll up mouse over the point, which is empty
                    self.setting = next(self.setting_pool)

        self.display_update()

    def clone(self):
        return GridPoint(
            self.x_offset,
            self.y_offset,
            self.setting_list)

    def reinit(self):
        self.setting = ''
        self.pieces = []
        self.elements = []

class PieceElement(GamePoint):
    # this is the basic constituent of a piece
    # it has a setting (colour in easy games)
    # it has a status indicator indicating where the piece is:
    #  'base', 'moving', 'attracted, 'installed'
    # it has a reference to its attachment grid_point when installed

    setting: str
    status: str
    rotation_status: int
    is_flipped: bool
    grid_point: GridPoint | None
    collision_rect: pygame.Rect
    offset_x: int
    offset_y: int

    def __init__(self, setting = '', x_offset=0, y_offset=0):
        super().__init__(x_offset, y_offset)

        # Create a surface for the sprite
        # Set the sprite's rect (position and size)

        self.setting = setting
        self.status = 'base'
        self.rotation_status = 0
        self.is_flipped = False
        self.grid_point = None
        # I define a collision rect that may be smaller
        self.collision_rect = pygame.Rect(self.rect) 

    def flip(self):
        self.is_flipped = not self.is_flipped

    # def clone(self):
    #     return PieceElement(self.setting, self.x_offset, self.y_offset)

class Piece(pygame.sprite.Group):

    # a piece is a subclass of Sprites group that groups several piece_elements
    # a Piece has a setting (colour), an origin element
    # it has a "unit_move" index to define its orientation

    setting: str
    status: str
    deck_position_x: int
    deck_position_y: int
    build_sequence: list
    local_move_list: list[str]
    local_move_length: int
    local_move_index: int
    bounding_rect: pygame.Rect
    origin: PieceElement

    def __init__(self,
                 setting,
                 deck_position_x=0,
                 deck_position_y=0,
                 piece_build_sequence = [],
                 local_move_list = []):
        
        super().__init__()

        self.setting = setting
        self.status = 'base'
        self.deck_position_x = deck_position_x
        self.deck_position_y = deck_position_y
        self.build_sequence = piece_build_sequence
        self.local_move_list = local_move_list
        self.local_move_length = len(local_move_list)
        self.local_move_index = 0
        self.origin = PieceElement()
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
    
    def reinit_to_deck(self):
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
    
    def rotate(self):
        for element in self.sprites():
            element.rotate(self.origin)
    
    def flip(self):
        pass

    def next_move(self, point_index, free_grid):
        if self.local_move_index < self.local_move_length - 1:
            self.next_local_move()
            return point_index
        
        #I have already made all local moves
        self.reinit_to_deck() #back to basic location
        point_index += 1
        try: #try next point in free_grid
            self.set_pos(free_grid[point_index])
            return point_index 
        except: #I tried all free points
            raise exc.FinalMove

    def next_local_move(self):
        for move in self.local_move_list[self.local_move_index].split(','):
            if move == 'r':
                self.rotate()
            elif move == 'f':
                self.flip()
            else:
                raise Exception
        self.local_move_index = (self.local_move_index + 1) % self.local_move_length

    def attach(self, elements_dict):
        self.status = 'installed'
        self.set_pos(elements_dict[self.origin])

        for element in self.sprites():
            element.status = 'installed'
            element.grid_point = elements_dict[element]
            if element not in element.grid_point.elements:
                element.grid_point.elements.append(element)
            if self not in element.grid_point.pieces:
                element.grid_point.pieces.append(self)
            
    def detach(self, target_status):
        # this function removes the piece from a grid.
        # the target status depends if I am handling movement
        # (in which case it is 'attracted') or solving puzzle
        # (in which case it is 'base')

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
        # just returns the dictionary of matching points 
        # which are not installed; keys are PieceElements, values are GridPoints 

        # let's test and handle collisions!
        collide_dict = pygame.sprite.groupcollide(
            self, grid, False, False, pygame.sprite.collide_rect_ratio(0.3))

        # remove occupied points 
        # or points whose setting does not correspond
        proper_dict = {}
        for element, point_list in collide_dict.items():
            for point in point_list:
                if point.setting != '':
                    if point.setting == element.setting:
                        proper_dict[element] = point
                    break
                if len(point.elements) == 0:
                    proper_dict[element] = point
                    break
                if element in point.elements:
                    proper_dict[element] = point
                    break

        return proper_dict

    def check_fit(self, grid):
        # test collision with the grid, returns a dictionary 
        # of attachment points and a success boolean
        points_dict = self.matching_points(grid)
        set_points = grid.set_points(self.setting)

        # if some grid points' setting is set,
        # check if all these points are matching
        if all((point in points_dict.values()) for point in set_points):
            # let's check if the whole piece fits in
            return all((element in points_dict.keys())
                       for element in self.sprites()), points_dict
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
                   
        elif self.status == 'attracted':  # i was attracted but not anymore
            self.status = 'moving'
            for element in self.sprites():
                element.status = 'moving'
                element.grid_point.pieces.remove(self)
                element.grid_point.elements.remove(element)
                element.grid_point = None
            
        grid.normalize(self,match_dict)

    def update(self, grid, event_list = []):
        # I override the update() method here,
        # to handle at piece level all the moving logics
        super().update()

        for event in event_list:
            # Handle group-level dragging logic
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # left mouse button is pressed
                    # mouse button is over a sprite in the piece
                    # and this is the piece I want to select
                    if self.is_clicked_piece(event):
                        if self.status == 'base':  
                            # the piece was in the deck, now it moves
                            # I register the relative position
                            # of mouse and of origin piece
                            self.origin.offset_x = self.origin.rect.centerx - \
                                event.pos[0]
                            self.origin.offset_y = self.origin.rect.centery - \
                                event.pos[1]
                            self.status = 'moving'
                            for element in self.sprites():
                                element.status = 'moving'

                        elif self.status == 'installed':  
                            # the piece was installed, i detach it
                            # I register the relative position
                            # of mouse and of origin piece
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
                    if self.status == 'moving':
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
        return any(sprite.rect.collidepoint(event.pos)
                   for sprite in self.sprites())

class Grid(pygame.sprite.Group):
    # Grid is a group of GridPoint
    # it has a grid offset for showing on the 2D screen,
    # which is th x and y of the origin point

    width: int
    height: int
    x_offset: int
    y_offset: int
    bounding_rect: pygame.Rect
     

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

    name: str
    complete_game: bool
    packing_value: int
    setting_list: list
    pieces_generator: dict
    grid: Grid
    pieces_dict: dict
    pieces_group: pygame.sprite.Group
    deck: list[Piece] = []
    known_failed_grids: list[int]
    
    icon: pygame.Surface
    caption: str
    screen: pygame.Surface
    theme: pygame_menu.Theme
    about_text: list[str]
    
    game_menu: pygame_menu.Menu
    solver_btn: pygame_menu.widgets.Button # type: ignore
    init_btn: pygame_menu.widgets.Button # type: ignore
    about_btn: pygame_menu.widgets.Button # type: ignore
    main_label: pygame_menu.widgets.Label # type: ignore
    exit_btn: pygame_menu.widgets.Button # type: ignore
    save_btn:  pygame_menu.widgets.Button # type: ignore
    load_btn:  pygame_menu.widgets.Button # type: ignore
    
    play_rect: pygame.Rect
    _grid_frame: pygame.Surface
    _grid_rect: pygame.Rect
    _deck_frame: pygame.Surface
    _deck_rect: pygame.Rect
    _grid_frame_width: int
    minimum_height: int
    minimum_width: int
    main_label_height: int
    _deck_rows: int
    _deck_columns: int
    running: bool
    
    def __init__(self,
                screen,
                icon_path = '',
                theme = MY_THEME,
                name = 'PuzzleGame',
                caption = 'Puzzle Game',
                about_text = ABOUT,
                complete_game = True,
                packing_value = 1,
                setting_list = [''],
                pieces_generator = {}):
        
        # set parameters
        self.name = name
        self.complete_game = complete_game
        self.packing_value = packing_value
        if icon_path == '':
            self.icon = pygame.Surface((10,10))
        else:
            self.icon = pygame.image.load(icon_path)
        self.caption = caption
        self.about_text = about_text
        self.setting_list = setting_list
        self.pieces_generator = pieces_generator
        self.known_failed_grids = []
        self.screen = screen
        self.theme = theme

        # build stuff
        self.build_grid()
        self.build_pieces()
        self.start_layout()
        
        # create a label timer
        self.label_timer = Label_Timer(duration = 3000)

        # it's running!
        self.running=True
    
    def reinit(self):
        self.grid.reinit()
        for piece in self.pieces_dict.values():
            piece.reinit_to_deck()
    
    def change_running(self):
        self.running = not self.running
    
    def start_layout(self):
        
        # ----------------------------------------------------------------------
        # Create menus:About
        # ----------------------------------------------------------------------
        
        _about_menu = pygame_menu.Menu(
            height=self.screen.get_height() * 0.6,
            title='About',
            width=self.screen.get_width() * 0.6
        )

        for m in self.about_text:
            _about_menu.add.label(m,
                                  align=pygame_menu.locals.ALIGN_CENTER, # type: ignore
                                  font_size=20)
            _about_menu.add.vertical_margin(30)

        # ---------------------------------------------------------------------
        # Create menus: load_config and _save_config
        # ----------------------------------------------------------------------
        
        _load_config_menu = pygame_menu.Menu(
            height=self.screen.get_height() * 0.6,
            title='Load Configuration',
            width=self.screen.get_width() * 0.6
        )
        
        _load_config_menu.add.label(
            title='Work in progress'
        )

        _save_config_menu = pygame_menu.Menu(
            title='Save Configuration',
            height=self.screen.get_height() * 0.6,
            width=self.screen.get_width() * 0.6            
        )

        _save_config_menu.add.label(
            title='Work in progress'
        )


        """
        Create main game menu
        Add buttons
        """

        self.game_menu = pygame_menu.Menu(
            title='Playing Puzzle Game',
            width=self.screen.get_width(),
            height=250,
            position=(0, 0),
            theme=self.theme,
            surface=self.screen,
            mouse_motion_selection=True)
        
        # Add twxo horizontal frames
        
        f1 = self.game_menu.add.frame_h(
            width=self.screen.get_width(),
            height=70,
            border_width=0,
            shadow_width=0)
        
        f2 = self.game_menu.add.frame_h(
            width=self.screen.get_width(),
            height=70,
            border_width=0,
            shadow_width=0)
        
        self.load_btn=f1.pack(
            self.game_menu.add.button(            
                'Load Config',
                _load_config_menu),
            align=pygame_menu.locals.ALIGN_LEFT)

        self.solver_btn = f1.pack(
            self.game_menu.add.button(
                'Run Solver',
                self.solve),
            align=pygame_menu.locals.ALIGN_CENTER)

        self.about_btn=f1.pack(
            self.game_menu.add.button(
                title='About',
                action=_about_menu),
            align=pygame_menu.locals.ALIGN_RIGHT)

        self.save_btn=f2.pack(
            self.game_menu.add.button(
                'Save Config',
                _save_config_menu),
            align=pygame_menu.locals.ALIGN_LEFT)

        self.init_btn=f2.pack(
            self.game_menu.add.button(
                title='Init',
                action=self.reinit),
            align=pygame_menu.locals.ALIGN_CENTER)
      
        self.exit_btn=f2.pack(
            self.game_menu.add.button(
                'Exit',
                action=self.change_running),
            align=pygame_menu.locals.ALIGN_RIGHT)

        #Store the label's height
        self.main_label_height = self.game_menu.get_height()

        #calculate minimum width and height, and the position of grid and deck
        grid_width = self.grid.bounding_rect.width
        grid_height = self.grid.bounding_rect.height
        
        max_piece_width: int = max(piece.bounding_rect.width
                                   for piece in self.pieces_dict.values())
        max_piece_height: int = max(piece.bounding_rect.height
                                    for piece in self.pieces_dict.values())
        
        self._deck_columns = 1
        num_pieces = len(self.pieces_dict.values())
        self._deck_rows = ceil(num_pieces/self._deck_columns)

        cumulated_pieces_height=self._deck_rows*max_piece_height

        while (cumulated_pieces_height + self.main_label_height >
               self.screen.get_height()):
            self._deck_columns += 1
            self._deck_rows = ceil(num_pieces/self._deck_columns)
            cumulated_pieces_height = self._deck_rows*max_piece_height

        grid_rect_width = round(
            self.screen.get_width()*(
            grid_width/
            (grid_width+(self._deck_columns*max_piece_width))))
        
        self.minimum_height = self.main_label_height + self._deck_rows*max_piece_height
        self.minimum_width = self.grid.bounding_rect.width + self._deck_columns*max_piece_width
       
        #create surface where deck and grid will be drawn
        self.play_frame = pygame.Surface((self.screen.get_width(),
                                          self.screen.get_height() - self.main_label_height))
        self.play_rect = self.play_frame.get_rect(topleft = (0, self.main_label_height))
        # self.play_frame.fill('white')

        # create surface where grid is drawn
        self._grid_frame = pygame.Surface(
            (
                grid_rect_width,
                self.screen.get_height()-self.main_label_height))
        self._grid_rect = self._grid_frame.get_rect(
            topleft=(0, self.main_label_height)
        )
        self._grid_frame.fill('white')
        pygame.draw.rect(
            self._grid_frame,
            (0,0,0),
            rect=(0,0,self._grid_rect.width, self._grid_rect.height),
            width=2,
            border_radius=30)

        # create surface where deck is drawn
        self._deck_frame = pygame.Surface(
            (
            self.screen.get_width()-self._grid_rect.width,
            self.screen.get_height()-self.main_label_height))
        self._deck_rect = self._deck_frame.get_rect(
            topleft=(self._grid_rect.width,self.main_label_height))
        self._deck_frame.fill('white')
        pygame.draw.rect(
            self._deck_frame,
            (0,0,0),
            (0,0,self._deck_rect.width,self._deck_rect.height),
            width=2,
            border_radius=30)

        #finally, position grid and deck correctly
        self.layout_update()

    def layout_update(self):
        self.position_grid()
        self.piece_distribute()

    def show(self):
        # fill the screen with a color to wipe away anything from last frame
        self.play_frame.fill("white")

        self.grid.update()
        for piece in self.pieces_dict.values():
            piece.update(grid = self.grid)

        #show the sprites
        self.grid.draw(self.play_frame)
        for piece in self.pieces_dict.values():
            piece.draw(self.play_frame)

        # flip() the display to put your work on screen
        pygame.display.flip()
        
    def draw(self, event_list):
        
        """
        update sprites
        """
        for piece in self.pieces_dict.values():
            piece.update(self.grid, event_list) #moving and rotating pieces, checking for collisions
        self.grid.update(event_list)

        """
        draw all background, show the sprites
        """
        self.screen.blit(self._grid_frame, self._grid_rect)
        self.screen.blit(self._deck_frame, self._deck_rect)
        self.grid.draw(surface=self.screen)
        self.pieces_group.draw(surface=self.screen)
        # self.draw_rects(self.play_frame)
        self.game_menu.draw(self.screen)
        
    def draw_rects(self, surface):
        pygame.draw.rect(surface, (255,0,0,255), self.grid.bounding_rect, 2)
        for element in self.pieces_group.sprites():
            pygame.draw.rect(surface, (255, 0, 0, 255), element.rect, 2)
        for element in self.grid.sprites():
            pygame.draw.rect(surface, (0, 0, 255, 255), element.rect, 1)
        for piece in self.pieces_dict.values():
            pygame.draw.rect(surface, (0, 255, 0, 255), piece.bounding_rect, 1)

    def build_grid(self):
        pass
    
    def build_pieces(self, piece_class = Piece):
        # generate pieces. I put pieces in a sprites group,
        # and also in a dictionary for easier browsing
        # WARNING ALL PIECES ARE IN 0 POSITION IN THIS REFERENCE METHOD,
        # NEED TO DISTRIBUTE
        
        self.pieces_group = pygame.sprite.Group()
        self.pieces_dict = {}

        for setting, piece_build_sequence in self.pieces_generator.items():
            new_piece = piece_class(
                setting,
                piece_build_sequence=piece_build_sequence)
            
            self.pieces_group.add(new_piece)
            self.pieces_dict[setting] = new_piece
    
    def position_grid(self):
        self.grid.compute_rect()
        
        x_padding: int = round(self._grid_rect.left 
                    +((self._grid_rect.width - self.grid.bounding_rect.width)/2 
                    +(self.grid.x_offset - self.grid.bounding_rect.left))) 
        y_padding: int = round(self._grid_rect.top
                    +(self._grid_rect.height - self.grid.bounding_rect.height)/2
                    +self.grid.bounding_rect.height
                    +(self.grid.y_offset - self.grid.bounding_rect.bottom))

        self.grid.x_offset = x_padding
        self.grid.y_offset = y_padding

        for point in self.grid.sprites():
            point.x_offset = x_padding
            point.y_offset = y_padding
            point.update_2D()

        self.grid.compute_rect()

    def save_config(self):
        pass

    def piece_distribute(self):
        num_pieces = len(self.pieces_dict.keys())

        cell_width = self._deck_rect.width/self._deck_columns
        cell_height = self._deck_rect.height/self._deck_rows

        cell_y = self._deck_rect.top
        cell_x = self._deck_rect.left
        x_index = 0
        y_index = 0

        for piece in self.pieces_dict.values():
            x_padding = (cell_width-piece.bounding_rect.width)/2
            y_padding = (cell_height-piece.bounding_rect.height)/2
            piece.set_2D(cell_x + x_padding +
                          piece.origin.rect.centerx - piece.bounding_rect.left, 
                         cell_y + y_padding + 
                         piece.bounding_rect.height + 
                         piece.origin.rect.centery - piece.bounding_rect.bottom)
            x_index = (x_index + 1) % self._deck_columns
            if x_index == 0:
                y_index = (y_index + 1) % self._deck_rows
            cell_x = self._deck_rect.left + x_index*cell_width
            cell_y = self._deck_rect.top + y_index*cell_height

    def build_deck(self, pieces_dict):
        """
        # takes the current status of the grid and of the pieces_dictionary, 
        and returns a list of pieces which are still not installed, for solving algorithm
        # pieces_dict is structured as {piece_name : piece}
        """
        self.deck = [piece for piece in pieces_dict.values()
                     if piece.status == 'base']

    """
    SOLVING FUNCTIONS
    """
    
    def solve(self):
        
        self.game_menu.set_title("SOLVING...")
        self.game_menu.draw(surface=self.screen)
        
        overlay = pygame.Surface(
            self.play_rect.size,
            pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(
            source=overlay,
            dest=self.play_rect.topleft)
        pygame.display.flip()
                                
        # whatever the status I need to change labels,
        # thus I need time management
        self.label_timer.start(start_time=pygame.time.get_ticks())
        
        self.build_deck(self.pieces_dict)
        self.known_failed_grids = []
            
        try :
            self.recursive_pose()
            current_time = pygame.time.get_ticks()
            self.game_menu.set_title(
                "SOLVED! - in {:.2f} seconds".format((
                    current_time-self.label_timer.start_time)/1000))
            self.label_timer.start(current_time)
        except exc.SolvingImpossibility:
            current_time = pygame.time.get_ticks()
            self.game_menu.set_title(
                "No solution found - searched for {:.2f} seconds".format((current_time-self.label_timer.start_time)/1000))
            self.label_timer.start(current_time)

    def recursive_pose(self, free_grid = None, deck = None):
        
        
        """
        the core of the solving program.
        Tries to fill the grid with pieces in the deck. 
        Returns the new grid and deck or exc.SolvingImpossibility if no solution is found
        """
        
        if free_grid is None:
            free_grid = self.grid.free_points()
        if deck is None:
            deck = self.deck

        if len(free_grid) == 0 or len(deck) == 0:  # no more free points or placed all pieces, cool!
            return

        # I have free points, let's continue
        # Put the pieces that have points with their colours set at beginning
        sorted_grid_list, free_grid, deck = self.optimize_grid_and_deck(free_grid, deck)                
        
        if len(free_grid) == 0 and len(deck) >0:
            raise exc.SolvingImpossibility
        
        if self.packing_value*len(free_grid) < sum((len(piece.sprites()) for piece in deck)):
            raise exc.SolvingImpossibility # there isn't enough space

        # I may already have encountered this grid, and it failed --> no use trying again!
        hash_value = self.my_hash(free_grid, deck)
        if hash_value in self.known_failed_grids:
            raise exc.SolvingImpossibility

        point_index = 0
        piece_index = 0
        current_piece = deck[piece_index]  # take the first piece in the deck
        current_piece.set_pos(free_grid[point_index])  # I place in first grid's free point

        # now is the main loop
        while_exit = False
        while not (while_exit):
            # try to put the current_piece on the grid
            success, fitting_points = current_piece.check_fit(self.grid)
            if success:  # it fits!
                current_piece.attach(fitting_points)
                deck.pop(piece_index)
                # now let's enter next recursion level
                try:
                    self.recursive_pose()
                    return True
                except exc.SolvingImpossibility:  # I didn't manage to solve the sub-grid
                    current_piece.detach('base')
                    # logically put the piece back in the deck
                    deck.insert(piece_index, current_piece)
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
        
        self.known_failed_grids.append(hash_value)
        raise exc.SolvingImpossibility

    def my_hash(self, point_list = [], deck = []):
        
        point_string_list = sorted([f"""{point.Hx}{point.Hy}{point.Hz}{point.setting}
                            {' '.join(f'{element.setting}{element.rotation_status}{element.is_flipped}' for element in point.elements)}"""
                              for point in point_list])
        
        piece_string_list = sorted([piece.setting for piece in deck])

        result = hash(''.join(point_string_list) + ''.join(piece_string_list))

        return result


    def optimize_grid_and_deck(self, free_grid, deck):

        set_settings_list = [point.setting for point in self.grid.sprites() if point.setting != '']
        deck.sort(key=lambda piece: piece.setting in set_settings_list, reverse=True)

        # let's analyse the split grid and optimise accordingly
        grid_list = self.grid_split(free_grid)
        sorted_grid_list = sorted(grid_list, key=lambda grid: len(grid))  # sort it

        if self.complete_game and len(sorted_grid_list[0]) < min([len(piece.sprites()) for piece in deck]):
            # it is a "complete" game (all points must be occupied) 
            # and the smallest sub-grid is smaller than the desk minimum
            raise exc.SolvingImpossibility
            
        while len(sorted_grid_list[0]) < min([len(piece.sprites()) for piece in deck]):
            #I can just remove the points of the sub_grid from the free grid
            for point in sorted_grid_list[0]:
                free_grid.remove(point)
            sorted_grid_list.pop(0)
            if len(sorted_grid_list) == 0:
                break
        
        return sorted_grid_list, free_grid, deck

    def group_distance(self, anchor_point, point_list):
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
