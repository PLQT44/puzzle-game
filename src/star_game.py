# Anne-Marie Stars' puzzle

# imports
import random
from itertools import permutations #needed for permutations of the deck
from pprint import pprint
import tkinter
import pygame
from main import RGB_COLOURS
import exceptions as exc

################################################################################
#                          CONSTANTS                                           #
################################################################################

X_GRID_OFFSET = 500
Y_GRID_OFFSET = 400
SCALE = 50
X_DECK_OFFSET = 50
Y_DECK_OFFSET = 620
PIECE_SPACING = 170

################################################################################
#                   GEOMETRY FUNCTIONS                                         #
################################################################################

def project_2D(coordinates, x_offset = 0, y_offset = 0):
	# transform the 3D coordinates in 2D according to plan geometry
	# I take into account screen geometry
	# entry is 3-tuplet, output is 2-tuplet
	x = coordinates[0]
	y = coordinates[1]
	z = coordinates[2]
	A = x_offset + SCALE*(x + y/2)
	B = y_offset - SCALE*(1.73*y/2)
	return (A,B)

def find_neighbour(anchor_point, grid):
	#I browse through the points of the grid to see if one is neighboring the given point
	# TODO DEFINE NEIGHBOURING TEST BETWEEN POINTS
	for point in grid.sprites():
		if point.neighbouring(anchor_point):
			return point

	raise exc.NoNeighbour

################################################################################
#                           CLASSES                                            #
################################################################################

class HexPoint(pygame.sprite.Sprite):
	# It is basically a sprite but with 3D hex capacities

	def update_2D(self):
		# when updating, I need to align 3D and 2D
		projected = project_2D((self.Hx, self.Hy, self.Hz), self.x_offset, self.y_offset)
		self.rect.x = projected[0]
		self.rect.y = projected[1]

	def __init__(self, Hx=0, Hy=0, Hz=0, x_offset = 0, y_offset = 0):
		super().__init__()

		self.image = pygame.Surface((1,1))

		# Each point has three 3D coordinates in Hexagonal plan.
		# Default creation is origin
		self.Hx = Hx
		self.Hy = Hy
		self.Hz = Hz

		# offset values correspond to the x,y location of the origin 3D point
		self.x_offset = x_offset
		self.y_offset = y_offset

		# Set the sprite's rect (position and size)
		self.rect = self.image.get_rect()
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

	def neighbouring(self, point):
		if (abs(self.Hx-point.Hx) + abs(self.Hy-point.Hy) + abs(self.Hz-point.Hz)) == 2:
			return True
		else:
			return False

	def update(self):
		self.update_2D()

	def clone(self):
		return HexPoint(self.Hx, self.Hy, self.Hz, self.x_offset, self.y_offset)

class GridPoint(HexPoint):
	# this is a point for a grid. I define it as a subclass of HexPoint
	# It has a number of specific properties
	# a status ('base', 'set', 'attracted', 'installed')
	# a reference to the occupying piece

	def __init__(self, Hx=0, Hy=0, Hz=0,
				x_offset= 0, y_offset = 0, radius = 10): #x_offset and y_offset are the x, y of the 3D origin point
		super().__init__(Hx, Hy, Hz, x_offset, y_offset)

		# Create a surface for the sprite - a 50*50 square with a black circle
		self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
		self.image.fill((255, 255, 255, 0))	 # Fill with transparent white

		#set the radius
		self.radius = radius

		#add a circle
		pygame.draw.circle(self.image, (0,0,0,255), (25,25), radius)

		# Each point has three 3D coordinates in Hexagonal plan.
		# Default creation is origin
		self.Hx = Hx
		self.Hy = Hy
		self.Hz = Hz

		# Set the sprite's rect (position and size)
		self.rect = self.image.get_rect()

		# I define x and y at init
		self.update_2D()

		# status and piece reference
		self.status = 'base'
		self.piece = None
	
	def show(self):
		message = f"Point {(self.Hx, self.Hy, self.Hz)}  status :  {self.status}  "

		if self.status == 'installed':
			message += self.piece.colour
		print(message)

	def update(self):
		super().update()

		if self.status == 'base':
			self.image.fill((255,255,255,0))
			pygame.draw.circle(self.image, (0,0,0,255), (25,25), self.radius)
			self.image.set_alpha(255)  # non-transparent
		elif self.status == 'attracted':
			self.image.fill((255,255,255,0))
			pygame.draw.circle(self.image, (0,0,0,255), (25,25), 1.5*self.radius)
			self.image.set_alpha(128) #semi transparent
		elif self.status == 'installed':
			self.image.set_alpha(0)

	def clone(self):
		return GridPoint(self.Hx, self.Hy, self.Hz, self.x_offset, self.y_offset)

	def reinit(self):
		self.status = 'base'
		self.piece = None

class PieceElement(HexPoint):
	# this is the basic constituent of a piece
	# it has a colour
	# it has a status indicator indicating where the piece is: 'base', 'moving', 'attracted, 'installed'
	# it has a reference to its attachment grid_point when installed

	def __init__(self, colour, Hx = 0, Hy = 0, Hz = 0, x_offset = 0, y_offset = 0):
		super().__init__(Hx, Hy, Hz, x_offset, y_offset)

		# Create a surface for the sprite - a star image
		self.image = pygame.image.load("./images/star_" + colour + ".png")

		# Set the sprite's rect (position and size)
		self.rect = self.image.get_rect()

		# I define x and y at init
		self.update_2D()

		self.colour = colour
		self.status = 'base'
		self.grid_point = None
		# additional properties for rotating star
		# self.clean_image = self.image
		# self.rotation = 0

	def show(self):
		pprint(vars(self))

	def update(self):
	## TODO INTRODUCE rotation system when attracted
		super().update()

		if self.status in ['base', 'installed']:
			# self.rotation = 0
			# rect = self.image.get_rect()
			# self.image = self.clean_image
			# self.rect = self.clean_image.get_rect(center = rect.center)
			self.image.set_alpha(255)
#		elif self.status == 'attracted':
			# self.rotation += 2
			# rect = self.image.get_rect()
			# clean_rect = self.clean_image.get_rect(center = rect.center)
			# print(rect.center)
			# self.image = pygame.transform.rotozoom(self.clean_image, self.rotation,1)
			# self.rect = self.image.get_rect(center = clean_rect.center)
			# self.image.set_alpha(128)
		else:
			self.image.set_alpha(128)

class Piece(pygame.sprite.Group):

	# a piece is a subclass of group that groups several piece_elements
	# a Piece has a colour, an origin element
	# it has a rotation indicator which is used when drawing,
	# or when calculating the fit onto the grid
	# I define also a deck_offset (x axis) which allows to put it
	# in a given place on the deck


	def __init__(self, colour, deck_position_x = 0, deck_position_y = 0, sequence = []):
		super().__init__()


		# Add first element to the group
		piece_element_1 = PieceElement(colour, x_offset = deck_position_x, y_offset = deck_position_y)
		self.add(piece_element_1)
		self.origin = piece_element_1

		# create elements based on sequence
		ref_elt = piece_element_1

		for move in sequence:
			new_element = PieceElement(colour = ref_elt.colour, Hx = ref_elt.Hx, Hy = ref_elt.Hy, Hz = ref_elt.Hz, x_offset = ref_elt.x_offset, y_offset = ref_elt.y_offset )
			method = getattr(new_element, "translate_" + move)
			method()
			new_element.update_2D() #this re-calculates 2D position of the new element
			self.add(new_element)
			ref_elt = new_element

		self.colour = colour
		self.rotation = 0
		self.status = 'base'
		self.deck_position_x = deck_position_x
		self.deck_position_y = deck_position_y

	def translate(self, vector = (0,0,0)):
		# translates all piece elements by vector
		for element in self.sprites():
			element.Hx += vector[0]
			element.Hy += vector[1]
			element.Hz += vector[2]

		self.update_2D()


	def rotate(self, angle = 1):
		# rotates all points around origine by	angle times Pi/3, trigonometric direction
		self.rotation += angle%6

		for i in range(angle):
			for element in self.sprites():
				if element != self.origin:
					element.rotate(self.origin)

		self.rotation = self.rotation%6

		self.update_2D()

	def reinit(self):

		# I set rotation to 0
		if self.rotation != 0:
			self.rotate(6-self.rotation)

		# I have to move everyone in 3D hex to origin
		vector = (-self.origin.Hx, -self.origin.Hy, -self.origin.Hz)
		self.translate(vector)

		self.update_2D()

	def reinit_to_deck(self):

		# it is basically the same as hex_init, plus back to deck in 2D

		# I set rotation to 0
		if self.rotation != 0:
			self.rotate(6-self.rotation)

		# I have to move everyone in 3D hex to origin
		vector = (-self.origin.Hx, -self.origin.Hy, -self.origin.Hz)
		self.translate(vector)

		for element in self.sprites():
			# change 2D reference of origin back to deck
			element.x_offset = self.deck_position_x
			element.y_offset = self.deck_position_y

			if element.status in ['attracted', 'installed']:
				element.grid_point.status = 'base'
				element.grid_point.piece = None

			element.grid_point = None
			element.status = 'base'

		self.status = 'base'
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

	def next_move(self):
		if self.rotation < 5:
			self.rotate()
		else:
			raise exc.FinalMove


	def show(self):
		print("\npiece : " + self.colour)
		print("rotation : " + str(self.rotation))
		print("origin : " + str((self.origin.Hx, self.origin.Hy, self.origin.Hz)))
		print("status : " + self.status)
		for element in self.sprites():
			element.show()

################### TO BE CHANGED IN ORDER TO ONLY TAKE IN PARAMETER THE ORIGIN ELEMENT ###############
################### WARNING IT DOES NOT LOGICALLY REMOVE FROM DECK WHEN ATTACHING ############################

	def attach(self, elements_dict):

		self.status = 'installed'

		self.origin.grid_point = elements_dict[self.origin]

		self.set_pos(self.origin.grid_point)

		for element in self.sprites():
			element.status = 'installed'
			element.grid_point = elements_dict[element]
			element.grid_point.status = 'installed'
			element.grid_point.piece = self


	def detach(self, target_status):
		#this function removes the piece from a grid.
		#the target status depends if I am handling movement (in which case it is 'attracted') or solving puzzle (in which case it is 'base')


		for element in self.sprites():
			element.grid_point.status = target_status
			if target_status == 'base':
				element.grid_point.piece = None
				element.grid_point = None
			element.status = target_status
			element.x_offset = self.origin.rect.x
			element.y_offset = self.origin.rect.y

		# I have to move everyone in 3D hex to origin
		vector = (-self.origin.Hx, -self.origin.Hy, -self.origin.Hz)
		self.translate(vector)

		#manage status
		self.status = target_status


	def matching_points(self, grid):
		# just returns the dictionary of matching points which are not installed

		#let's test and handle collisions!
		collide_dict = pygame.sprite.groupcollide(self, grid, False, False, pygame.sprite.collide_rect_ratio(0.3))

		#remove occupied points
		proper_dict = {}
		for element, point_list in collide_dict.items():
			for point in point_list:
				if point.status in ['base', 'attracted']:
					proper_dict[element] = point
				break

		return proper_dict

	def check_fit(self, grid):
		#basically the same as before 2D graphics management. test collision with the grid, returns a dictionary of attachment points and a status

		points_dict = self.matching_points(grid)

		# let's check if the whole piece fits in
		return all((element in points_dict.keys()) for element in self.sprites()), points_dict

	def update(self, event_list, grid, *args, **kwargs):

		# I override the update() method here, to handle at piece level all the moving logics

		super().update()

		for event in event_list:
			# Handle group-level dragging logic
			if event.type == pygame.MOUSEBUTTONDOWN:
					if event.button == 1:  # left mouse button is pressed
						if any(sprite.rect.collidepoint(event.pos) for sprite in self.sprites()): #mouse button is over a sprite in the piece

							if self.status == 'base': #the piece was in the deck, now it moves
								# I register the relative position of mouse and of origin piece
								self.origin.offset_x = self.origin.rect.x - event.pos[0]
								self.origin.offset_y = self.origin.rect.y - event.pos[1]
								self.status = 'moving'
								for element in self.sprites():
									element.status = 'moving'

							elif self.status == 'installed': #the piece was installed, i detach it
								# I register the relative position of mouse and of origin piece
								self.origin.offset_x = self.origin.rect.x - event.pos[0]
								self.origin.offset_y = self.origin.rect.y - event.pos[1]
								self.detach('attracted')


					elif event.button == 3: #right button pressed
						if self.status in ['moving', 'attracted']:
							self.rotate()

							match, match_dict = self.check_fit(grid)

							if match:
								self.status = 'attracted'
								for element in self.sprites():
									element.status = 'attracted'
									element.grid_point = match_dict[element]
									element.grid_point.status = 'attracted'
							else:
								if self.status == 'attracted': #i was attracted but that's not the case anymore
									for element in self.sprites():
										element.status = 'moving'
										element.grid_point.status = 'base'
										element.grid_point = None
									self.status = 'moving'

							grid.normalize(match_dict)


			elif event.type == pygame.MOUSEBUTTONUP:
				if event.button == 1:
					if self.status == 'moving':
						self.reinit_to_deck()

					elif self.status == 'attracted':
						match, match_dict = self.check_fit(grid)
						self.attach(match_dict)

			elif event.type == pygame.MOUSEMOTION:
				if self.status in ['moving', 'attracted']: # actually dragging

					new_origin_x = pygame.mouse.get_pos()[0] + self.origin.offset_x
					new_origin_y = pygame.mouse.get_pos()[1] + self.origin.offset_y

					for element in self.sprites(): # all elements move like origin
						element.x_offset = new_origin_x
						element.y_offset = new_origin_y

					match, match_dict = self.check_fit(grid)

					if match:
						self.status = 'attracted'
						for element in self.sprites():
							element.status = 'attracted'
							element.grid_point = match_dict[element]
							element.grid_point.status = 'attracted'
							element.grid_point.piece = self

					else:
						if self.status == 'attracted': #i was attracted but that's not the case anymore
							for element in self.sprites():
								element.status = 'moving'
								element.grid_point.status = 'base'
								element.grid_point.piece = None
								element.grid_point = None
							self.status = 'moving'

					grid.normalize(match_dict)

class Grid(pygame.sprite.Group):
	# Grid is a group of GridPoint
	# it has a grid offset for showing on the 2D screen, which is th x and y of the origin point


	def __init__(self, width=0, height=0, x_offset = 0, y_offset = 0, point_list = []):
		super().__init__()
		# Each grid has a height (Y axis once projected on 2D)
		# and a width (X axis)
		self.width = width
		self.height = height
		self.x_offset = x_offset
		self.y_offset = y_offset

		for Y in range(height):
			P = GridPoint(x_offset = x_offset, y_offset = y_offset) #initiate point at origin

			P.translate_nw(Y)

			if Y % 2 == 0:
				P.translate_e(round(Y/2))
				local_width = width-1  #even  rows are smaller
			else:
				P.translate_e(round((Y-1)/2))
				local_width = width

			P.update_2D() #I moved it in 3D hex space, need to set 2D
			self.add(P)

			for X in range(local_width):
				new_P = P.clone()
				new_P.translate_e()
				P.update_2D()
				self.add(new_P)
				P = new_P

			P.kill()

		for point in point_list:
			self.add(point)


	def show(self):
		print("\nGrid origin %s / %s" % (str(self.x_offset), str(self.y_offset)))
		for point in self.sprites():
			point.show()		

	def normalize(self, attracted_points):
		#attracted_points is a dictionary of piece elements with attracted point
		#browse through the points, if point has status activated but not in the activated list, then back to 'base' status

		for grid_point in self.sprites():
			if (grid_point.status == 'attracted') and not(grid_point in attracted_points.values()):
				grid_point.status = 'base'


	def free_points(self):
		# returns a list of free points
		# not completely sure this is of any use, maybe to speed up
		# will evolve to free_sub_grids

		return [point for point in self.sprites() if point.status == 'base']


	def reinit(self):
		for point in self.sprites():
			if point.status == 'installed':
				point.piece.reinit_to_deck()
			point.reinit()


	def recursive_pose(self, deck, do_split = True, complete = True):

		#the core of the solving program. Tries to fill the grid with pieces in the deck. Returns the deck or exc.SolvingImpossibility if no solution is found
		#230914 this version is by far the best! I do not enter into sub-grid recursion, but I use the split to check if I have impossible sub-grids, in which case I exit
		#I should try a new version ranking free points based on their proximity to installed pieces

		free_grid = self.free_points()
		
		if len(free_grid) == 0: #no more free points, cool!
			print("\nNo more free points, I completed the grid!")
			return deck
				
		#I have free points, let's continue
		
		#A little bit of shuffling to change
		random.shuffle(deck) 
				
		#first, let's split, to test if there are very small sub-grids, in which case we need to exit
		grid_list = grid_split(self)
		sorted_grid_list = sorted(grid_list, key=lambda grid: len(grid)) #sort it
		
		#check if the number of free points is superior to the smallest piece, otherwise exit immediatly
		if len(sorted_grid_list[0]) < min([len(piece.sprites()) for piece in deck]):
			print("\nSmallest sub-grid too small for the deck, exit immediatly")
			raise exc.SolvingImpossibility
		
		print("\n*************************\nEntering recursive pose\n*************************")
		print("\nStatus of current solving grid and deck : " + str(complete))
		show(self, deck)
		
		random.shuffle(free_grid)
		point_index = 0	
		current_point = free_grid[point_index] #let's start with first free point
		
		piece_index = 0
		current_piece = deck[piece_index] #take the first piece in the deck

		#choose a piece that is smaller than the free grid. If none, exit
		while_exit = False
		
		while not(while_exit):
			if len(free_grid) < len(current_piece.sprites()):
				if complete:
					print("\nGrid too small for the piece, exit immediatly")
					while_exit = True
					raise exc.SolvingImpossibility
				else:
					piece_index += 1
					current_piece = deck[piece_index] #take the next piece in the deck
			else:
				while_exit = True
		
		#I chose a correct piece, let's put it in position
		current_piece.set_pos(current_point) #I place in first grid's free point
		
		#now is the main loop
		while_exit = False
		
		while not(while_exit):
			
			print("\nTrying %s piece on point" % current_piece.colour)
			current_point.show()
										
			#try to put the current_piece on the grid
			success, fitting_points = current_piece.check_fit(self)

			if success: #it fits!
			
				print("\nManaged to put %s piece " % current_piece.colour)
				current_piece.attach(fitting_points)
				deck.remove(current_piece)
			
				#now let's enter next recursion level
				try :
					print("\nEntering next recursion level")
					next_deck = self.recursive_pose(deck)
					while_exit = True
					return next_deck
			
				except exc.SolvingImpossibility: #I didn't manage to solve the sub-grid
					print("\nDidn't manage to solve sub-grid")
					current_piece.detach('base')
					deck.insert(piece_index, current_piece) #logically put the piece back in the deck
					
					#I need to make the next move for piece
					try: #try to rotate once more
						print("\nTrying to rotate")
						current_piece.next_move()
						print("\n%s piece rotation is now %s" % (current_piece.colour.title(), str(current_piece.rotation))) 
					except exc.FinalMove: #I already went through all rotations
						current_piece.reinit_to_deck() #back to basic location
						try: #try to move to next free point
							point_index += 1
							print("\nTrying to move to next point")
							current_point = free_grid[point_index]
							print("\nNext point is")
							current_point.show()
							current_piece.set_pos(current_point)
						except: #I tried all free points
							if complete: #this is a complete grid, so I should be able to put the piece somewhere
								while_exit = True
								raise exc.SolvingImpossibility
							else:
								try: #maybe with next piece?
									print("\nTrying to pick next piece")
									piece_index += 1
									current_piece = deck[piece_index]
									print("\nPiece is now " + current_piece.colour)
									point_index = 0
									current_point = free_grid[point_index]
									print("\nNext point is")
									current_point.show()
									current_piece.set_pos(current_point)
								except: #this is really the end
									while_exit = True
									raise exc.SolvingImpossibility

			else: #if piece does not fit, I move to next possibility ; first rotate, then try to translate, then try with next piece

				try: #try to rotate once more
					print("\nTrying to rotate")
					current_piece.next_move()
					print("\n%s piece rotation is now %s" % (current_piece.colour.title(), str(current_piece.rotation))) 
				except exc.FinalMove: #I already went through all rotations
					current_piece.reinit_to_deck() #back to basic location
					try: #try to move to next free point
						point_index += 1
						print("\nTrying to move to next point")
						current_point = free_grid[point_index]
						print("Next point is")
						current_point.show()
						current_piece.set_pos(current_point)
					except: #I tried all free points
						if complete: #this is a complete grid, so I should be able to put the piece somewhere
							while_exit = True
							raise exc.SolvingImpossibility
						else:
							try: #maybe with next piece?
								print("\nTrying to pick next piece")
								piece_index += 1
								current_piece = deck[piece_index]
								print("Piece is now " + current_piece.colour)
								point_index = 0
								current_point = free_grid[point_index]
								print("Next point is")
								current_point.show()
								current_piece.set_pos(current_point)
							except: #this is really the end
								while_exit = True
								raise exc.SolvingImpossibility

		
################################################################################
#					ULTIMATE RECURSION FUNCTIONS							   #
################################################################################

def multi_recursive_pose(grid_list, deck):

	sorted_grid_list = sorted(grid_list, key=lambda grid: len(grid))
	first_sub_grid = sorted_grid_list.pop(0)
	while_exit = False
	possible_decks = permutations(deck)
	current_deck = list(next(possible_decks)) #start the iterator

	while not(while_exit):
		try:
			# print("\nIn multi recursive pose, here is the first sub grid")
			# first_sub_grid.show()
			# print("\nAnd here is the desk")
			# for piece in deck:
				# print(piece.colour, end=" ")
			# # input("\nPress Enter")

			#if this is the last grid to solve, then first piece must fit
			if len(sorted_grid_list) == 0:
				complete = True
			else:
				complete = False
			
			next_deck = first_sub_grid.recursive_pose(current_deck, False, complete)
			
			# print("\nIn multi_recursive_pose, I solved the first sub-grid!")
			
			#we need to try the rest of the grids. If it works, fine! else, we need to change the way to solve the first sub-grid, end try again. I do that by permutating the deck.
			try:
				if len(sorted_grid_list) == 0:
					return first_sub_grid, next_deck
				else:
					new_next_grid, new_next_deck = multi_recursive_pose(sorted_grid_list, next_deck)
					first_sub_grid.add(new_next_grid)
					# print("\nThis should be end of multi recursion")
					# show(first_sub_grid, new_next_deck)
					# input("\nPress Enter")
					return first_sub_grid, new_next_deck
			
			except exc.SolvingImpossibility: #couldn't solve the next grid with the way the first sub grid was solved
				first_sub_grid.reinit() #remove all pieces, set points to 'base' status
				try:
					print("\nTrying to permutate the deck")
					current_deck = list(next(possible_decks)) #I start again with a permutated deck
				except StopIteration as e: #I tried all permutations of the deck, and the whole branch is, in fact, unsolvable
					# print("\All permutations tried")
					while_exit = True

		except exc.SolvingImpossibility: 
			# print("\n#couldn't solve the smallest grid, no possibility to solve the list of grids")
			# input("Press Enter")
			while_exit = True
	
	raise exc.SolvingImpossibility

def grid_split(target_grid, anchor_grid = None):
	# separates a grid in a list of independent sub-grids of free points
	#anchor_list is an grid containing points from which I try to expand in grid
	
	free_list = list(target_grid.free_points())
	remaining_points_number = len(free_list)

	if remaining_points_number == 0: #no free point, answer is null
		if anchor_grid is None:
			return []
		else:
			return [anchor_grid]

	else: #there are at least 1 free points in target_grid, I can evaluate neighbouring and start recursion
		
		result_grid = Grid(x_offset = target_grid.x_offset, y_offset = target_grid.y_offset)
		
		#let's concentrate on free points of target_grid
		for point in target_grid.sprites():
			if point.status == 'base':
				result_grid.add(point)
		
		if anchor_grid is None: #create the initial point to grow from
			anchor_grid = Grid(x_offset = target_grid.x_offset, y_offset = target_grid.y_offset, point_list = [free_list[0]])
		
		for anchor_point in anchor_grid.sprites():
		
			#anchor point is outside of grid	
			result_grid.remove(anchor_point)
			
			try: #let's try to find a neighbour to the anchor point
				neighbour = find_neighbour(anchor_point, result_grid)
				
				#if I find a neighbour, I start recursing, anchoring in that neighbour
				anchor_grid.add(neighbour)
				result_grid.remove(neighbour)
				result = grid_split(result_grid, anchor_grid)
				return result
				
			except exc.NoNeighbour: #anchor_point has no neighbour --> I will check with another point in anchor_grid. If all anchor points have been tried, I have an independant grid
				pass
		
		#no point in anchor grid has a neighbour in result_grid
		result = [anchor_grid] + grid_split(result_grid)
		# print("\Here is the result of split")
		# for grid in result:
			# grid.show()
		return result


################################################################################
#                    BUILDING FUNCTIONS                                        #
################################################################################

def piece_generation(generator, piece_generation_x, piece_generation_y, piece_spacing):
	#generate pieces. I put pieces in a sprites group, and also in a dictionary for easier browsing
	pieces_group = pygame.sprite.Group()
	pieces_dict = {}
	
	for colour, moves in generator.items():
		new_piece = Piece(colour = colour, deck_position_x = piece_generation_x, deck_position_y = piece_generation_y, sequence = moves)
		pieces_group.add(new_piece)
		pieces_dict[colour] = new_piece
		piece_generation_x += piece_spacing #regular spacing of pieces in the deck
		
	return pieces_group, pieces_dict

def build_deck(pieces_dict, grid):
	#takes the current status of the grid and of the pieces_dictionary, and returns a list of pieces which are still not installed, for solving algorithm
	#pieces_dict is structured as {piece_name : piece}

	return [piece for piece in pieces_dict.values() if piece.status == 'base']


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


def create_piece_image(piece):
	#I add several stars to create a new image for a piece, adapting to colour

	# open the basic star image
	star = tkinter.Image.open("./images/star_" + piece.colour + ".png")
	star.show()

	#initiate what will be the final image
	piece_image = star

	# the unit distance is 45 pixel
	# I also need to know the image height. Star is 50 height
	offset = 45
	height = piece_image.height

	for point in piece.reference_array[1:]:
		# loop in all the pieces' points except the first one
		# expand image to be able to add a new star
		piece_image = tkinter.ImageOps.expand(piece_image,
									  border=(0,50,50,0),
									  fill=(255,255,255,0))

		# project and adapt point to offset
		(A,B) = project_2D(point)
		a = int(offset*A)
		b = int(height - offset*B)

		# pasting star on piece_image
		piece_image.paste(star,(a,b),star)

		# to show specified image
		piece_image.show()
		piece_image = piece_image.crop(piece_image.getbbox())
		height = piece_image.height

	piece_image.save("./images/piece_" + piece.colour + ".png")

################################################################################
######################### DEBUG FUNCTIONS ######################################
################################################################################

def deck_show(deck):
	print("\nDeck length : " + str(len(deck)))
	for piece in deck:
		print(piece.colour)
		# piece.show()

def show(grid, deck):
	grid.show()
	deck_show(deck)
	
	# # fill the screen with a color to wipe away anything from last frame
	# screen.fill("white")

	# grid.update()
	# pieces_group.update()

	# #show the sprites
	# grid.draw(screen)
	# pieces_group.draw(screen)

	# # flip() the display to put your work on screen
	# pygame.display.flip()
		
	# input("press Enter to continue")


