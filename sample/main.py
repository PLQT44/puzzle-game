# Anne-Marie Stars' puzzle

# imports
from typing import Optional
import pygame
import pygame_menu
import sys
from constants import RGB_COLOURS, WINDOW_SIZE
import exceptions as exc
# import puzzles.puzzle_game
# import puzzles.star_game
# import puzzles.bubble_game

#global references and constants

REFERENCE_MESSAGE = "Press Enter to Solve, 'I' to init"
GAME_NAME = ['Star']
ABOUT = ['Author : Pierre LANQUETOT',
         'Enjoy!']

clock: Optional['pygame.time.Clock'] = None
main_menu: Optional['pygame_menu.Menu'] = None
screen: Optional['pygame.Surface'] = None
game = None

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

def change_game_name(value, game_name):
    """
    change the name of the puzzle type

    value is the tuple returned by the selection menu
    game_name is a string
    """
    selected, index = value
    print(f'Selected puzzle : {game_name} at index {index}')
    GAME_NAME[0] = game_name

    
def create_game(game_choice):
    try:
        # Dynamically import the chosen puzzle module
        puzzle_module = __import__('puzzles.' + game_choice[0].lower() + "_game", fromlist=[''])
        return getattr(puzzle_module, game_choice[0].capitalize()+"Game")()
    except ImportError:
        raise ImportError("Puzzle not found")

def play_game(game_name):

    # Define globals
    global screen
    global game
    global main_menu
    global clock
    
    #disable the main menu, I am playing
    main_menu.disable()
    main_menu.full_reset()

    #start the game
    game = create_game(game_name)
    game.main_message = REFERENCE_MESSAGE
    game.start(WINDOW_SIZE[0], WINDOW_SIZE[1], REFERENCE_MESSAGE)

    # load and set the logo TO BE ADAPTED WITH CHOSEN GAME
    pygame.display.set_icon(game.icon)
    pygame.display.set_caption(game.caption)

    # create a label timer
    label_timer = Label_Timer(duration = 3000)

    # Main loop
    running = True
    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        event_list = pygame.event.get()
        for e in event_list:
            if e.type == pygame.QUIT:
                exit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    main_menu.enable()
                    return

        # # pass events to main menu
        # if main_menu.is_enabled():
        #     main_menu.update(event_list)

        # Flip surface
        running = handle_main_events(running, screen, game, event_list, label_timer)
                    
        # fill the screen with a color to wipe away anything from last frame
        screen.fill("white")
        #manage label timer and show message
        if not label_timer.update_state(pygame.time.get_ticks()):
            game.main_message = REFERENCE_MESSAGE
            
        #mask previous text
        game.update_main_label(game.main_message)

        #draw everything
        game.draw(event_list, screen)
        
        # flip() the display to put your work on screen
        pygame.display.flip()

        # limits FPS to 60
        clock.tick(60) / 1000


def execute_main():
    
    #-------------------------------------------------------------------------
    # Globals
    #-------------------------------------------------------------------------
    global clock
    global main_menu
    global screen
    global game

    # pygame setup
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    clock = pygame.time.Clock()
    running = True
    
    #--------------------------------------------------------------------------
    # Create menus : Play Menu
    #--------------------------------------------------------------------------

    play_menu = pygame_menu.Menu(
        height=WINDOW_SIZE[1] * 0.7,
        title='Play Menu',
        width=WINDOW_SIZE[0] * 0.75
    )

    play_menu.add.button('Start',  # When pressing return -> play_game(GAME_NAME[0])
                         play_game,
                         GAME_NAME)
    play_menu.add.selector('Select game ',
                           [('1 - Star', 'Star'),
                            ('2 - Bubble', 'Bubble')],
                           onchange=change_game_name,
                           selector_id='select_game')
    play_menu.add.button('Return to main menu', pygame_menu.events.BACK)

    # -------------------------------------------------------------------------
    # Create menus:About
    # -------------------------------------------------------------------------
    
    about_menu = pygame_menu.Menu(
        height=WINDOW_SIZE[1] * 0.6,
        title='About',
        width=WINDOW_SIZE[0] * 0.6
    )

    for m in ABOUT:
        about_menu.add.label(m, align=pygame_menu.locals.ALIGN_LEFT, font_size=20)
    about_menu.add.vertical_margin(30)
    about_menu.add.button('Return to menu', pygame_menu.events.BACK)
    
    #----------------------------------------------------------------------------
    # Create menus : Main Menu
    #----------------------------------------------------------------------------

    main_menu = pygame_menu.Menu('Welcome', 400, 300,
                       theme=pygame_menu.themes.THEME_BLUE)

    main_menu.add.button('Select and Play', play_menu)
    main_menu.add.button('About', about_menu)
    main_menu.add.button('Quit', pygame_menu.events.EXIT)

    # Main loop
    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        event_list = pygame.event.get()
        for event in event_list:
            if event.type == pygame.QUIT:
                running = False

        # Main menu
        if main_menu.is_enabled():
            main_menu.mainloop(screen)

        # Flip surface
        pygame.display.flip()

        # limits FPS to 60
        clock.tick(60) / 1000

    pygame.quit()

def handle_main_events(running, screen, game, event_list, label_timer):
    
    for event in event_list:
        if event.type == pygame.QUIT:
            running = False
              
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                game.update_main_label("SOLVING...")
                game.draw(event_list, screen)
                overlay = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 128))
                screen.blit(overlay, (0,0))
                pygame.display.flip()
                                
                #whatever the status I need to change labels, thus I need time management
                label_timer.start(pygame.time.get_ticks())
                try :
                    game.solve(screen)
                    current_time = pygame.time.get_ticks() #calculation may take some time
                    game.main_message = "SOLVED! - in {:.2f} seconds".format((current_time-label_timer.start_time)/1000)
                    label_timer.start(current_time)
                except exc.SolvingImpossibility:
                    current_time = pygame.time.get_ticks() #calculation may take some time
                    game.main_message = "No solution found - searched for {:.2f} seconds".format((current_time-label_timer.start_time)/1000)
                    label_timer.start(current_time)
                                                    
            elif event.key == pygame.K_i:
                game.main_message = "Let's start all over again"
                label_timer.start(pygame.time.get_ticks())
                game.reinit()
        
    return running

if __name__ == "__main__": 
    execute_main()