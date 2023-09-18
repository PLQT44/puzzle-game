# Anne-Marie Stars' puzzle

# imports
import random
from itertools import permutations, cycle #needed for permutations of the deck
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

	def distance(self, point):
		#well, it is the square of distance in 3D hex space...
		return (abs(self.Hx-point.Hx) + abs(self.Hy-point.Hy) + abs(self.Hz-point.Hz))

	def neighbouring(self, point):
		return (self.distance(point) == 2)

	def update(self):
		self.update_2D()

	def clone(self):
		return HexPoint(self.Hx, self.Hy, self.Hz, self.x_offset, self.y_offset)

class GridPoint(HexPoint):
	# this is a point for a grid. I define it as a subclass of HexPoint
	# It has a number of specific properties
	# a status ('base', 'attracted', 'installed')
	# it has a colour that is basically set to '' but can browse throuh an iterator, also include a reference list which indicates how to handle specification of a colour
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

		# what can be the set status
		self.set_colour_pool = cycle(['', 'orange', 'yellow', 'green', 'violet', 'pink', 'red', 'blue'])

		# status and piece reference
		self.status = 'base'
		self.colour = next(self.set_colour_pool)
		self.piece = None
	
	def show(self):
		message = f"Point {(self.Hx, self.Hy, self.Hz)}  \tstatus :  {self.status} \tcolour : {self.colour} "
		if self.status == 'installed':
			message += f"\tInstalled piece : {self.piece.colour}"
		print(message)

	def update(self, event_list = []):
		super().update()
		
		for event in event_list:
			#handle setting logic
			if event.type == pygame.MOUSEBUTTONDOWN:
				if (event.button == 4
		 			and self.rect.collidepoint(event.pos)
		 			and self.status in ['base', 'set']): #roulet scroll up mouse over the point
					self.colour = next(self.set_colour_pool)

		self.image.fill((255,255,255,0))

		if self.status == 'base':
			pygame.draw.circle(self.image, (0,0,0,255), (25,25), self.radius)
			self.image.set_alpha(255)  # non-transparent
		elif self.status == 'attracted':
			pygame.draw.circle(self.image, (0,0,0,128), (25,25), 1.5*self.radius)
			self.image.set_alpha(128) #semi transparent
		elif self.status == 'installed':
			self.image.set_alpha(0)
		
		if self.colour != '':		
			self.image = pygame.image.load("./images/star_" + self.colour + ".png")
			self.image.set_alpha(128)
		
	def clone(self):
		return GridPoint(self.Hx, self.Hy, self.Hz, self.x_offset, self.y_offset)

	def reinit(self):
		self.status = 'base'
		self.colour = ''
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

		# create elements based on sequence of moves
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

	def next_move(self, point_index, free_grid):
		if self.rotation < 5:
			self.rotate()
			return point_index, free_grid[point_index]
		#I have already made all rotations
		self.reinit_to_deck() #back to basic location
		point_index += 1
		try: #try next point in free_grid
			current_point = free_grid[point_index]
			self.set_pos(current_point)
			return point_index, current_point 
		except: #I tried all free points
			raise exc.SolvingImpossibility

	def show(self):
		print("\npiece : " + self.colour)
		print("rotation : " + str(self.rotation))
		print("origin : " + str((self.origin.Hx, self.origin.Hy, self.origin.Hz)))
		print("status : " + self.status)
		for element in self.sprites():
			element.show()

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
				if ((point.status in ['base', 'attracted'] and point.colour == '') or (point.colour == element.colour)):
					proper_dict[element] = point
				break

		return proper_dict

	def check_fit(self, grid):
		#basically the same as before 2D graphics management. test collision with the grid, returns a dictionary of attachment points and a success boolean
		points_dict = self.matching_points(grid)
		set_points = grid.set_points(self.colour)

		#check if all points in set_points are in matching dict
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
							#update the matching status
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
				if self.status in ['moving', 'attracted']: # actually dragging
					new_origin_x = pygame.mouse.get_pos()[0] + self.origin.offset_x
					new_origin_y = pygame.mouse.get_pos()[1] + self.origin.offset_y
					for element in self.sprites(): # all elements move like origin
						element.x_offset = new_origin_x
						element.y_offset = new_origin_y

					#update matching status
					match, match_dict = self.check_fit(grid)
					self.status_update(match, match_dict, grid)

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

	def set_points(self, colour = ''):
		if colour == '':
			return []
		else:
			return [point for point in self.sprites() if point.colour == colour]

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