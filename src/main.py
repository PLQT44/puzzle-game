# Anne-Marie Stars' puzzle

# imports
import numpy as np
import datetime
import pygame
import sys
import exceptions as exc
import star_game as game
import solving

#global references and constants
RGB_COLOURS = {'orange':(255,128,0), 'blue':(0,0,255),
			   'violet':(127,0,255), 'pink':(255,0,255),
			   'red':(255,0,0), 'green':(0,255,0),
			   'yellow':(255,255,0), 'black' : (0,0,0)}

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720

REFERENCE_MESSAGE = "Press Enter to Solve, 'I' to init"

# create function for updating and showing the main label
def update_main_label(screen, text, text_rect, font, message = REFERENCE_MESSAGE):
	
	#mask previous text
	text.fill("white")
	screen.blit(text, text_rect)

	#show new text
	text = font.render(message, True, RGB_COLOURS['black'])  # Text, antialiasing, color
	text_rect = text.get_rect()
	text_rect.center = (SCREEN_WIDTH // 2, 50)  # Center the text
	screen.blit(text, text_rect)	

def execute_main():
	# Initiate the play_grid
	play_grid = game.Grid(width =7, height = 4, x_offset = 500, y_offset = 400) #create a new grid

	#generate pieces. I put pieces in a sprites group, and also in a dictionary for easier browsing
	piece_generator = { "red" : ['ne', 'se', 'ne'], "green" : ['e', 'e', 'ne'], "pink" : ['ne', 'e', 'se'], "blue" : ['ne', 'se', 'e'], "yellow" : ['e', 'ne', 'se'], "violet" : ['e', 'e'], "orange" : ['e', 'ne']}

	pieces_group, pieces_dict = game.piece_generation(piece_generator, game.X_DECK_OFFSET, game.Y_DECK_OFFSET, game.PIECE_SPACING)

	# pygame setup
	pygame.init()
	
	screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
	clock = pygame.time.Clock()
	running = True
	dt = 0

	# load and set the logo
	logo = pygame.image.load("./images/Star_icon_stylized.svg.png")
	pygame.display.set_icon(logo)
	pygame.display.set_caption("Stars puzzle")

	# Initiate message
	main_message = REFERENCE_MESSAGE

	main_font = pygame.font.Font(None, 36)
	main_text = main_font.render(REFERENCE_MESSAGE, True, RGB_COLOURS['black'])  # Text, antialiasing, color
	main_text_rect = main_text.get_rect()
	main_text_rect.center = (SCREEN_WIDTH // 2, 50)  # Center the text

	# create a label timer
	label_timer_active = False
	label_timer_duration = 3000  # 3 seconds (in milliseconds)
	start_time = 0


	while running:
		# poll for events
		# pygame.QUIT event means the user clicked X to close your window

		event_list = pygame.event.get()
		current_time = pygame.time.get_ticks()

		for event in event_list:
			if event.type == pygame.QUIT:
				running = False
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_RETURN:
					sys.stdout = open('solving_log.txt', 'w')
					update_main_label(screen, main_text, main_text_rect, main_font, "SOLVING...")
					overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
					overlay.fill((0, 0, 0, 128))
					screen.blit(overlay, (0,0))
					pygame.display.flip()
					play_deck = game.build_deck(pieces_dict, play_grid)
					
					#whatever the status I need to change labels, thus I need time management
					label_timer_active = True
					start_time = current_time

					try :
						play_grid, play_deck = solving.recursive_pose(play_grid, play_deck)
						current_time = pygame.time.get_ticks() #calculation may take some time
						main_message = "SOLVED! - in {:.2f} seconds".format((current_time-start_time)/1000)
						start_time = current_time
					except exc.SolvingImpossibility:
						current_time = pygame.time.get_ticks() #calculation may take some time
						main_message = "No solution found - searched for {:.2f} seconds".format((current_time-start_time)/1000)
						start_time = current_time
					
					sys.stdout.close()
					
				elif event.key == pygame.K_i:
					main_message = "Let's start all over again"
					label_timer_active = True
					start_time = current_time
					play_grid.reinit()
					for piece in pieces_dict.values():
						piece.reinit_to_deck()

		# fill the screen with a color to wipe away anything from last frame
		screen.fill("white")

		for piece in pieces_dict.values():
			piece.update(event_list, play_grid) #moving and rotating pieces, checking for collisions

		play_grid.update(event_list)

		#show the sprites
		play_grid.draw(screen)
		pieces_group.draw(screen)

		#manage label timer and show message
		if label_timer_active and current_time - start_time >= label_timer_duration:
			main_message = REFERENCE_MESSAGE

		#mask previous text
		update_main_label(screen, main_text, main_text_rect, main_font, main_message)
		
		# flip() the display to put your work on screen
		pygame.display.flip()

		# limits FPS to 60
		clock.tick(60) / 1000

	pygame.quit()


if __name__ == "__main__": 
    execute_main()