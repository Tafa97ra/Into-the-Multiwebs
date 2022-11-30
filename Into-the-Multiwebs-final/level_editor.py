import pygame
import pickle
from os import path


pygame.init()

clock = pygame.time.Clock()
fps = 60

#game window
tile_size = 30
cols = 40
margin = 100
screen_width = tile_size * cols
screen_height = (tile_size * cols // 2) + margin

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Level Editor')


#load images
sun_img = pygame.image.load('images/sun.png')
sun_img = pygame.transform.scale(sun_img, (tile_size, tile_size))
bg_img = pygame.image.load('images/nightsky.jpg')
bg_img = pygame.transform.scale(bg_img, (screen_width, screen_height - margin))
dirt_img = pygame.image.load('images/dirt.png')
grass_img = pygame.image.load('images/grass.png')

lava_img = pygame.image.load('images/lava.png')
lava_img = pygame.transform.scale(lava_img, (tile_size, tile_size // 2))

malwareA_img = pygame.image.load('images/hugevirus.png')
malwareB_img = pygame.image.load('images/virus.png')

platform_x_img = pygame.image.load('images/platform_x.png')
platform_y_img = pygame.image.load('images/platform_y.png')

#lava_img = pygame.image.load('images/lava.png')
coin_img = pygame.image.load('images/coin.png')
life_img = pygame.image.load('images/life.png')
antivirus_img = pygame.image.load('images/antivirus.png')


exit_img = pygame.image.load('images/exit.png')
save_img = pygame.image.load('images/save_btn.png')
load_img = pygame.image.load('images/load_btn.png')

portal_good_img = pygame.image.load('images/portal_good.png')
portal_good_o_img = pygame.image.load('images/portal_good_out.png')
portal_bad_img = pygame.image.load('images/portal_bad.png')
portal_bad_o_img = pygame.image.load('images/portal_bad_out.png')
acp_img = pygame.image.load("images/accesspoint.png")
bcp_img = pygame.image.load("images/badpoint.png")

bully_img = pygame.image.load("images/cyberbully.jpg")

#define game variables
clicked = False
level = 1

#define colours
white = (255, 255, 255)
green = (144, 201, 120)

font = pygame.font.SysFont('Futura', 24)

#create empty tile list
world_data = []
for row in range(20):
	r = [0] * 40
	world_data.append(r)


#create boundary
for y in range(0, 20):
    for x in range(0, 40):
        if x == 0 or y == 0 or x == 39 or y == 19:
            world_data[y][x] = 1

#function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

def draw_grid():
	for c in range(41):
		#vertical lines
		pygame.draw.line(screen, white, (c * tile_size, 0), (c * tile_size, screen_height - margin))
		#horizontal lines
		pygame.draw.line(screen, white, (0, c * tile_size), (screen_width, c * tile_size))


def draw_world():
	for row in range(20):
		for col in range(40):
			if world_data[row][col] > 0:
				if world_data[row][col] == 1:
					#dirt blocks
					img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 2:
					#grass blocks
					img = pygame.transform.scale(grass_img, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 3:
					# Malware A
					img = pygame.transform.scale(malwareA_img, (tile_size, int(tile_size)))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 4:
					# Malware B
					img = pygame.transform.scale(malwareB_img, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 5:
					#exit
					img = pygame.transform.scale(exit_img, (tile_size, int(tile_size * 1.5)))
					screen.blit(img, (col * tile_size, row * tile_size - (tile_size // 2)))
				if world_data[row][col] == 6:
					#coin
					img = pygame.transform.scale(coin_img, (tile_size // 2, tile_size // 2))
					screen.blit(img, (col * tile_size + (tile_size // 4), row * tile_size + (tile_size // 4)))
				if world_data[row][col] == 7:
					#horizontally moving platform
					img = pygame.transform.scale(platform_x_img, (tile_size, tile_size // 2))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 8:
					#vertically moving platform
					img = pygame.transform.scale(platform_y_img, (tile_size, tile_size // 2))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 9:
					# good portal
					img = pygame.transform.scale(portal_good_img, (tile_size, int(tile_size * 1.5)))
					screen.blit(img, (col * tile_size, row * tile_size - (tile_size // 2)))
				if world_data[row][col] == 10:
					# good portal out
					img = pygame.transform.scale(portal_good_o_img, (tile_size, int(tile_size * 1.5)))
					screen.blit(img, (col * tile_size, row * tile_size - (tile_size // 2)))
				if world_data[row][col] == 11:
					# bad portal
					img = pygame.transform.scale(portal_bad_img, (tile_size, int(tile_size * 1.5)))
					screen.blit(img, (col * tile_size, row * tile_size - (tile_size // 2)))
				if world_data[row][col] == 12:
					# bad portal out
					img = pygame.transform.scale(portal_bad_o_img, (tile_size, int(tile_size * 1.5)))
					screen.blit(img, (col * tile_size, row * tile_size - (tile_size // 2)))
				if world_data[row][col] == 13:
					# extra life
					img = pygame.transform.scale(life_img, (tile_size // 2, tile_size // 2))
					screen.blit(img, (col * tile_size + (tile_size // 4), row * tile_size + (tile_size // 4)))
				if world_data[row][col] == 14:
					# antivirus
					img = pygame.transform.scale(antivirus_img, (tile_size // 2, tile_size // 2))
					screen.blit(img, (col * tile_size + (tile_size // 4), row * tile_size + (tile_size // 4)))
				if world_data[row][col] == 15:
					# access point
					img = pygame.transform.scale(acp_img, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size - tile_size // 2))
				if world_data[row][col] == 16:
					# bad access point
					img = pygame.transform.scale(bcp_img, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size - tile_size // 2))
				if world_data[row][col] == 17:
					# dark web 
					img = pygame.transform.scale(lava_img, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size + tile_size // 2))
				if world_data[row][col] == 18:
					# cyberbully
					img = pygame.transform.scale(bully_img, (2 * tile_size, 2 * tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 19:
					# report button
					img = pygame.transform.scale(portal_bad_o_img, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				
				"""
				if world_data[row][col] == 18:
					# x platform
					img = pygame.transform.scale(platform_x_img, (tile_size, tile_size // 2))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 19:
					# x platform
					img = pygame.transform.scale(platform_y_img, (tile_size, tile_size // 2))
					screen.blit(img, (col * tile_size, row * tile_size))
				"""



class Button():
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self):
		action = False

		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button
		screen.blit(self.image, (self.rect.x, self.rect.y))

		return action

#create load and save buttons
save_button = Button(screen_width // 2 - 150, screen_height - 80, save_img)
load_button = Button(screen_width // 2 + 50, screen_height - 80, load_img)

#main game loop
run = True
while run:

	clock.tick(fps)

	#draw background
	screen.fill(green)
	screen.blit(bg_img, (0, 0))
	screen.blit(sun_img, (tile_size * 2, tile_size * 2))

	#load and save level
	if save_button.draw():
		#save level data
		pickle_out = open(f'levels/level{level}_data', 'wb')
		pickle.dump(world_data, pickle_out)
		pickle_out.close()
	if load_button.draw():
		#load in level data
		if path.exists(f'levels/level{level}_data'):
			pickle_in = open(f'levels/level{level}_data', 'rb')
			world_data = pickle.load(pickle_in)


	#show the grid and draw the level tiles
	draw_grid()
	draw_world()


	#text showing current level
	draw_text(f'Level: {level}', font, white, tile_size, screen_height - 60)
	draw_text('Press UP or DOWN to change level', font, white, tile_size, screen_height - 40)

	#event handler
	for event in pygame.event.get():
		#quit game
		if event.type == pygame.QUIT:
			run = False
		#mouseclicks to change tiles
		if event.type == pygame.MOUSEBUTTONDOWN and clicked == False:
			clicked = True
			pos = pygame.mouse.get_pos()
			x = pos[0] // tile_size
			y = pos[1] // tile_size
			#check that the coordinates are within the tile area
			if x < 40 and y < 20:
				#update tile value
				if pygame.mouse.get_pressed()[0] == 1:
					world_data[y][x] += 1
					if world_data[y][x] > 19:
						world_data[y][x] = 0
				elif pygame.mouse.get_pressed()[2] == 1:
					world_data[y][x] -= 1
					if world_data[y][x] < 0:
						world_data[y][x] = 19
		if event.type == pygame.MOUSEBUTTONUP:
			clicked = False
		#up and down key presses to change level number
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_UP:
				level += 1
			elif event.key == pygame.K_DOWN and level > 1:
				level -= 1

	#update game display window
	pygame.display.update()

pygame.quit()