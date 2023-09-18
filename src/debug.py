#imports

import pygame

################################################################################
######################### DEBUG FUNCTIONS ######################################
################################################################################

def deck_show(deck):
	print("\nDeck length : " + str(len(deck)))
	for piece in deck:
		print(piece.colour)
		# piece.show()

def show(grid, deck, surface):
	grid.show()
	deck_show(deck)
	
	# fill the screen with a color to wipe away anything from last frame
	surface.fill("white")

	grid.update()
	for piece in deck:
		piece.update()

	#show the sprites
	grid.draw(surface)
	for piece in deck:
		piece.draw(surface)

	# flip() the display to put your work on screen
	pygame.display.flip()
		
	# input("press Enter to continue")
