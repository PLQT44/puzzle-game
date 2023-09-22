# Anne-Marie Stars' puzzle

# imports
import pygame
import sys
from constants import RGB_COLOURS, SCREEN_WIDTH, SCREEN_HEIGHT
import exceptions as exc
import puzzles.puzzle_game
import puzzles.star_game

#global references and constants

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

def choose_game():
	return puzzles.star_game.StarGame()

def execute_main():
	
	# pygame setup
	pygame.init()
	screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
	clock = pygame.time.Clock()
	running = True

	#CHOOSE GAME
	game = choose_game()
	game.start(SCREEN_WIDTH, SCREEN_HEIGHT)

	# load and set the logo TO BE ADAPTED WITH CHOSEN GAME
	pygame.display.set_icon(game.icon)
	pygame.display.set_caption(game.caption)

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
					update_main_label(screen, main_text, main_text_rect, main_font, "SOLVING...")
					overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
					overlay.fill((0, 0, 0, 128))
					screen.blit(overlay, (0,0))
					pygame.display.flip()
					
					#whatever the status I need to change labels, thus I need time management
					label_timer_active = True
					start_time = current_time
					try :
						game.solve()
						current_time = pygame.time.get_ticks() #calculation may take some time
						main_message = "SOLVED! - in {:.2f} seconds".format((current_time-start_time)/1000)
						start_time = current_time
					except exc.SolvingImpossibility:
						current_time = pygame.time.get_ticks() #calculation may take some time
						main_message = "No solution found - searched for {:.2f} seconds".format((current_time-start_time)/1000)
						start_time = current_time
										
				elif event.key == pygame.K_i:
					main_message = "Let's start all over again"
					label_timer_active = True
					start_time = current_time
					game.reinit()
					
		# fill the screen with a color to wipe away anything from last frame
		screen.fill("white")
		game.draw(event_list, screen)

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