# Anne-Marie Stars' puzzle

# imports
from ast import main
import pygame
import pygame_menu
import sys
from constants import RGB_COLOURS, WINDOW_SIZE
import exceptions as exc

#global references and constants

GAME_NAME = ['Star']
ABOUT = [
    'Author : Pierre LANQUETOT',
    'Created : 2023 september',
    'Enjoy!']

clock: pygame.time.Clock
main_menu: pygame_menu.Menu
screen: pygame.Surface
game = None

def change_game_name(value, game_name):
    """
    change the name of the puzzle type

    value is the tuple returned by the selection menu
    game_name is a string
    """
    selected,  index = value
    print(f'Selected puzzle : {game_name} at index {index}')
    GAME_NAME[0] = game_name

    
def create_game(game_choice):
    
    global screen
    
    try:
        # Dynamically import the chosen puzzle module
        puzzle_module = __import__('puzzles.' + game_choice[0].lower() + "_game", fromlist=[''])
        return getattr(puzzle_module, game_choice[0].capitalize()+"Game")(screen)
    except ImportError:
        raise ImportError("Puzzle not found")

def play_game(game_name):

    # Define globals
    global screen
    global main_menu
    global game
    global clock
    
    #disable the main menu, I am playing
    main_menu.disable()
    main_menu.full_reset()

    #start the game
    game = create_game(game_name)

    # load and set the logo TO BE ADAPTED WITH CHOSEN GAME
    pygame.display.set_icon(game.icon)
    pygame.display.set_caption(game.caption)

    # Main loop
    while game.running:
        # poll for events
        event_list = pygame.event.get()
        for e in event_list:
            if e.type == pygame.QUIT:
                exit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    main_menu.enable()
                    return
            elif e.type == pygame.VIDEORESIZE:
                game.layout_update(e.size)
                
        #manage label timer 
        if not game.label_timer.update_state(pygame.time.get_ticks()):
            game.game_menu.set_title(f'Playing {game.name}')
            
        if game.game_menu.is_enabled():
            game.game_menu.update(event_list)
        
        #draw playing items
        game.play_frame.fill((0,0,0,0))
        game.draw(event_list)
        
        # flip() the display to put your work on screen
        pygame.display.flip()

        # limits FPS to 60
        clock.tick(60)
    
    main_menu.enable()


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
    screen = pygame.display.set_mode(
        WINDOW_SIZE,
        flags=pygame.RESIZABLE)
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

    play_menu.add.button(
        'Start',  # When pressing return -> play_game(GAME_NAME[0])
        play_game,
        GAME_NAME)
    
    play_menu.add.selector('Select game ',
                           [
                               ('1 - Star', 'Star'),
                               ('2 - Bubble', 'Bubble')],
                           onchange=change_game_name,
                           selector_id='select_game')
    
    play_menu.add.button(
        'Return to main menu',
        pygame_menu.events.BACK) # type: ignore

    # -------------------------------------------------------------------------
    # Create menus:About
    # -------------------------------------------------------------------------
    
    about_menu = pygame_menu.Menu(
        height=WINDOW_SIZE[1] * 0.6,
        title='About',
        width=WINDOW_SIZE[0] * 0.6
    )

    for m in ABOUT:
        about_menu.add.label(
            m,
            align=pygame_menu.locals.ALIGN_LEFT, # type: ignore
            font_size=20)
        about_menu.add.vertical_margin(30)
    
    #---------------------------------------------------------------------------# Create menus : Main Menu
    #----------------------------------------------------------------------------

    main_menu = pygame_menu.Menu(
        'Welcome',
        400,
        300)

    main_menu.add.button('Select and Play', play_menu)
    main_menu.add.button('About', about_menu)
    main_menu.add.button('Quit', pygame_menu.events.EXIT) # type: ignore

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
        clock.tick(60)

    pygame.quit()

def handle_main_events(running, screen, game, event_list, label_timer):
    
    for event in event_list:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                game.solve()
                                                    
            elif event.key == pygame.K_i:
                game.main_message = "Let's start all over again"
                label_timer.start(pygame.time.get_ticks())
                game.reinit()
        
    return running

if __name__ == "__main__": 
    execute_main()