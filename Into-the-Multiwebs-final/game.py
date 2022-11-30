import time
import pygame
from pygame.locals import *
from pygame import mixer
import pickle
from os import path
import random


#########################################################################################################################
## Initialization ##
#########################################################################################################################

pygame.mixer.pre_init(44100, -16, 2, 512)

mixer.init()
pygame.init()

# set frame rate
clock = pygame.time.Clock()
fps = 60

# Define screen
screen_width = 1200
screen_height = 600

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Tutorial")

#########################################################################################################################
## Game Variables ##
#########################################################################################################################

#define fonts
fontA = pygame.font.SysFont('Bauhaus 93', 60)
font_score = pygame.font.SysFont('Bauhaus 93', 21)
font_malware = pygame.font.SysFont('Bauhaus 93', 40)
font_tutorial = pygame.font.SysFont('Bauhaus 93', 25)

# define colours
white = (255, 255, 255)
green = (0, 255, 0)
red = (255, 0, 0)
orange = (255, 191, 0)
grey = (200, 200, 200)



# define game variables
tile_size = 30
game_over = 0
main_menu = True
pause_menu = False
access_pt = False
mini_game = False
bully_beat = False
download_menu = False
from_pause = 0
loss_menu = False
win_menu = False


level = 11
max_levels = 12
score = 0
lives = 3

origin = [2 * tile_size, screen_height - 150]
check_point = origin
portal_exits = []
bully_port = []

player_speed = 4        # default = 4
malware = False
cooldown = 40


# load images
sun_img = pygame.image.load('images/sun.png')
#bg_img = pygame.image.load('images/sky.png')
bg_img = pygame.image.load('images/nightsky.jpg')
#bg_img = pygame.image.load('images/index.jpeg')
#bg_img = pygame.image.load('images/background.png')
bg_full_img = pygame.transform.scale(bg_img, (1200, 600))

restart_image = pygame.image.load("images/restart_btn.png")
start_image = pygame.image.load("images/start_btn.png")
start_image = pygame.transform.scale(start_image, (tile_size * 4, tile_size * 2))
exit_image = pygame.image.load("images/exit_btn.png")
exit_image = pygame.transform.scale(exit_image, (tile_size * 4, tile_size * 2))
done_btn_img = pygame.image.load("images/done.png")
done_btn_img = pygame.transform.scale(done_btn_img, (tile_size, tile_size))
pwd_btn_img = pygame.image.load("images/changepassword.png")
pwd_btn_img = pygame.transform.scale(pwd_btn_img, (int(3.4 * tile_size), tile_size))
dwnld_img = pygame.image.load("images/download.png")
dwnld_img = pygame.transform.scale(dwnld_img, (int(3.4 * tile_size), tile_size))
buy_life_img = pygame.image.load("images/buylife.png")
buy_life_img = pygame.transform.scale(buy_life_img, (3 * tile_size, tile_size))
buy_av_img = pygame.image.load("images/buyantivirus.png")
buy_av_img = pygame.transform.scale(buy_av_img, (3 * tile_size, tile_size))


# load sounds
bg_music = pygame.mixer.music.load("images/what-is-this-called.wav")
pygame.mixer.music.play(-1, 0.0, 5000)
coin_fx = pygame.mixer.Sound("images/coin.wav")
coin_fx.set_volume(0.5)
jump_fx = pygame.mixer.Sound("images/jump.wav")
jump_fx.set_volume(0.5)
gameover_fx = pygame.mixer.Sound("images/game_over.wav")
gameover_fx.set_volume(0.5)




#########################################################################################################################
## Methods ##
#########################################################################################################################


# draw text 
def draw_text(text, font, text_col, x, y):
    image = font.render(text, True, text_col)
    screen.blit(image, (x,y))

def level_text(level):
    # 3, 13
    first_line_row = 3 * tile_size
    x = 13 * tile_size

    if path.exists(f'levels/level_{level}.txt'):
        level_file = open(f'levels/level_{level}.txt', 'r')
        row_num = 0
        for line in level_file.readlines():
            line = line[:-1]
            draw_text(line, font_tutorial, grey, x, first_line_row)
            first_line_row += 30

        level_file.close()


# Reset level
def reset_level(level):
    global portal_exits
    global bully_port
    bully_port = []
    portal_exits = []
    player.reset(check_point[0], check_point[1])
    malwareA_group.empty()
    malwareB_group.empty()
    exit_group.empty()
    good_o_portals.empty()
    good_portals.empty()
    report_group.empty()
    bad_portals.empty()
    coin_group.empty()
    lives_group.empty()
    antivirus_group.empty()
    acp_group.empty()
    lava_group.empty()
    bcp_group.empty()
    platform_group.empty()
    bully_group.empty()

    if path.exists(f'levels/level{level}_data'):
        pickle_in = open(f'levels/level{level}_data', 'rb')
        world_data = pickle.load(pickle_in)

    world = World(world_data)

    return world

def has_lives(lives):
    return lives > 0

def has_malware(malware):
    if malware:
        global cooldown
        cooldown = 10
        return 3
    return player_speed
         
#########################################################################################################################
#########################################################################################################################
## Main Game Classes ##
#########################################################################################################################



#########################################################################################################################
## Button ##

# Button
class Button():

    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False
        # get mouse position
        pos = pygame.mouse.get_pos()

        # check mouse over + click
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # draw button
        screen.blit(self.image, self.rect)

        return action

#########################################################################################################################
## Player ##
class Player():
    def __init__(self, x, y):
        self.reset(x, y)
        self.lives = 3
        

    def update(self, game_over):

        
        dx = 0
        dy = 0
        walk_cooldown = 5
        col_thresh = 10
        global malware
        global score
        global lives
        global access_pt
        global mini_game

        if game_over == 0:

            # get key presses
            key = pygame.key.get_pressed()
            if (key[pygame.K_SPACE]) and self.jumped == False and self.airbourne == False:
                jump_fx.play()
                self.vel_y = -12
                self.jumped = True
            
            if (key[pygame.K_SPACE] == False): 
                self.jumped = False

            if key[pygame.K_LEFT]:
                dx -= has_malware(malware)
                self.counter += 1
                self.direction = -1

            if key[pygame.K_RIGHT]:
                dx += has_malware(malware)
                self.counter += 1
                self.direction = 1

            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            #handle animation
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == -1:
                    self.image = self.images_left[self.index]
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                

            # add gravity
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10

            dy += self.vel_y

            # check for collision
            self.airbourne = True
            for tile in world.tile_list:
                # check x-collision
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # check y-collision
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if self.vel_y < 0:          # jumping collision
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    elif self.vel_y >= 0:       # falling collision
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.airbourne = False




            # update pos
            self.rect.x += dx
            self.rect.y += dy

            # boundary collision
            if self.rect.bottom > (screen_height):
                self.rect.bottom = (screen_height)
                dy = 0

            """
            # check for platform collision
            for platform in platform_group:
                # x collision
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # y collision
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # below platform
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top
                    # above platform
                    elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
                        self.rect.bottom = platform.rect.top
                        dy = 0
            """
            
            # check for dark web collision
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1
                gameover_fx.play()

            # check for malwareA collision
            if pygame.sprite.spritecollide(self, malwareA_group, False):
                game_over = -1
                gameover_fx.play()

            # check for malwareB collision
            if pygame.sprite.spritecollide(self, malwareB_group, True):
                # Add rand int for rand effect
                malware = True
                if score > 10:
                    score -= 10
                else:
                    score = 0
            
            # check for exit collision
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1

            # check good link collision + interaction
            if pygame.sprite.spritecollide(self, good_portals, False):
                if key[pygame.K_DOWN]:
                    player.reset(portal_exits[0][0], portal_exits[0][1])

            # check bad link collision + interaction
            if pygame.sprite.spritecollide(self, bad_portals, False):
                if key[pygame.K_DOWN]:
                    malware = True
                    if score > 10:
                        score -= 10
                    else:
                        score = 0
                    player.reset(2 * tile_size, screen_height - 150)

            # check collision with extra life
            if pygame.sprite.spritecollide(self, lives_group, True):
                lives += 1

            # check collision with anitvirus
            if pygame.sprite.spritecollide(self, antivirus_group, True):
                malware = False

            # check for acces point collision + interaction
            if pygame.sprite.spritecollide(self, acp_group, False):
                if key[pygame.K_DOWN]:
                    access_pt = True
                    check_point[0] = self.rect.x
                    check_point[1] = self.rect.y

            # check for bad point collision + interaction
            if pygame.sprite.spritecollide(self, bcp_group, False):
                if key[pygame.K_DOWN]:
                    malware = True
                    score -= random.randint(1, (score//3))

            # check for report button collision and interaction
            if pygame.sprite.spritecollide(self, report_group, False):
                if key[pygame.K_DOWN]:
                    mini_game = True
                    
            

            

        elif game_over == -1:
            self.image = self.ghost
            self.rect.y -= 5
            

        #draws player
        screen.blit(self.image, self.rect)
    
        return game_over
        
    def reset(self, x, y):
        global malware

        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0

        for num in range(1, 5):
            img_right = pygame.image.load(f'images/guy{num}.png')        
            img_right = pygame.transform.scale(img_right, (20, 40))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)

        self.ghost = pygame.image.load("images/ghost.png")
        self.ghost = pygame.transform.scale(self.ghost, (tile_size, tile_size))
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.height = self.image.get_height()
        self.width = self.image.get_width()
        self.rect.x = x
        self.rect.y = y
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.airbourne = True
        


#########################################################################################################################
## World ##
def draw_grid():
    for line in range(0, 60):
        pygame.draw.line(screen, (255, 255, 255), (0, line * tile_size), (screen_width, line * tile_size))
        pygame.draw.line(screen, (255, 255, 255), (line * tile_size,0), (line * tile_size, screen_height))
        
class World():
    def __init__(self, data):
        self.tile_list = []

        #load images
        dirt_img = pygame.image.load('images/block.png')
        grass_img = pygame.image.load('images/block2.png')

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                # dirt block
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                # grass block
                if tile == 2:
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                # MalwareA
                if tile == 3:
                    malwareA = MalwareA(col_count * tile_size, row_count * tile_size)
                    malwareA_group.add(malwareA)
                # Malware B
                if tile == 4:
                    malwareB = MalwareB(col_count * tile_size, row_count * tile_size)
                    malwareB_group.add(malwareB)
                # Exit
                if tile == 5:
                    exit = Exit(col_count * tile_size, row_count * tile_size - tile_size // 2)
                    exit_group.add(exit)
                # Coins 
                if tile == 6:
                    coin = Coin(col_count * tile_size + tile_size // 2, row_count * tile_size + tile_size // 2)
                    coin_group.add(coin)
                # good link 
                if tile == 9:
                    portal = Portal_G(col_count * tile_size + tile_size // 2, row_count * tile_size)
                    good_portals.add(portal)
                # good link exit
                if tile == 10:
                    portal = Portal_G_O(col_count * tile_size + tile_size // 2, row_count * tile_size )
                    good_o_portals.add(portal)
                    portal_exits.append([(col_count * tile_size + tile_size//2), (row_count * tile_size + tile_size//2)])
                # bad link
                if tile == 11:
                    portal = Portal_B(col_count * tile_size + tile_size // 2, row_count * tile_size)
                    bad_portals.add(portal)
                # bad link exit
                if tile == 12:
                    portal = Portal_B_O(col_count * tile_size, row_count * tile_size - tile_size // 2)
                    bad_portals.add(portal)
                # extra life
                if tile == 13:
                    life = Life(col_count * tile_size + tile_size // 2, row_count * tile_size + tile_size //2)
                    lives_group.add(life)
                # anti virus
                if tile == 14:
                    antiV = Antivirus(col_count * tile_size + tile_size // 2, row_count * tile_size + tile_size // 2)
                    antivirus_group.add(antiV)
                # access point
                if tile == 15:
                    acp = Access_Point(col_count * tile_size + tile_size // 2, row_count * tile_size - tile_size // 4 )
                    acp_group.add(acp)
                # bad access point
                if tile == 16:
                    bcp = Bad_Point(col_count * tile_size + tile_size // 2, row_count * tile_size - tile_size // 4 )
                    bcp_group.add(bcp)
                # dark web
                if tile == 17:
                    lava = Lava(col_count * tile_size, row_count * tile_size + tile_size // 2)
                    lava_group.add(lava)
                # cyberbully
                if tile == 18:
                    bully = Bully(col_count * tile_size, row_count * tile_size)
                    bully_group.add(bully)
                    #bully_rect = bully.rect
                    tile = (bully.image, bully.rect)
                    self.tile_list.append(tile)
                    bully_port.append([(col_count + 2) * tile_size, row_count * tile_size])
                # report button
                if tile == 19:
                    report = Portal_B_O(col_count * tile_size + tile_size // 2, row_count * tile_size + tile_size // 2)
                    report_group.add(report)
                
                """
                # platform x
                if tile == 18:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 1, 0)
                    platform_group.add(platform)
                # platform x
                if tile == 19:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 0, 1)
                    platform_group.add(platform)
                """

                

                col_count += 1
            row_count += 1
    
    def draw(self):
        
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            pygame.draw.rect(screen, (255, 255, 255), tile[1], 1)

#########################################################################################################################
#########################################################################################################################
## Sprite Classes ##
#########################################################################################################################
#########################################################################################################################


#########################################################################################################################
## Enemy Classes ##
#########################################################################################################################

# Malware A Class
class MalwareA(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("images/hugevirus.png")
        self.image = pygame.transform.scale(self.image, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > tile_size:
            self.move_direction *= -1
            self.move_counter *= -1

# Malware B class
class MalwareB(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("images/virus.png")
        self.image = pygame.transform.scale(self.image, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > tile_size:
            self.move_direction *= -1
            self.move_counter *= -1


class Bully(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("images/cyberbully.jpg")
        self.image = pygame.transform.scale(self.image, (2* tile_size, 2 * tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        

# Lava Class

class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("images/lava.png")
        self.image = pygame.transform.scale(self.image, (tile_size, tile_size//2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("images/platform.png")
        self.image = pygame.transform.scale(img, (tile_size, tile_size//2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0
        self.move_x = move_x
        self.move_y = move_y

    def update(self):
        self.rect.x += self.move_direction * self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.move_counter += 1
        if abs(self.move_counter) > tile_size:
            self.move_direction *= -1
            self.move_counter *= -1




#########################################################################################################################
## Collectibles Classes ##
#########################################################################################################################

# coin class
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("images/coin2.png")
        self.image = pygame.transform.scale(self.image, (tile_size//2, tile_size//2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

class Highscore(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("images/coin2.png")
        self.image = pygame.transform.scale(self.image, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

# life class
class Life(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("images/life.png")
        self.image = pygame.transform.scale(self.image, (tile_size//2, tile_size//2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

# anitvirus class
class Antivirus(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("images/antivirus.png")
        self.image = pygame.transform.scale(self.image, (tile_size//2, tile_size//2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

#########################################################################################################################
## Portal Classes
#########################################################################################################################

# Level exit class
class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("images/exit.png")
        self.image = pygame.transform.scale(self.image, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Good link Class
class Portal_G(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("images/goodportal.png")
        self.image = pygame.transform.scale(self.image, (tile_size * 2, int(tile_size)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

# Good link exit Class
class Portal_G_O(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("images/goodportalexit.png")
        self.image = pygame.transform.scale(self.image, (tile_size // 2, int(tile_size // 3 * 2)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

# Bad portal class
class Portal_B(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("images/badportal.png")
        self.image = pygame.transform.scale(self.image, (tile_size * 2, int(tile_size)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


# Bad portal exit class
class Portal_B_O(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("images/badportalexit.png")
        self.image = pygame.transform.scale(self.image, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.center = x, y
        
        

class Access_Point(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("images/accesspoint.png")
        self.image = pygame.transform.scale(self.image, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

class Bad_Point(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("images/badpoint.png")
        self.image = pygame.transform.scale(self.image, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


#########################################################################################################################
## Rendering ##
#########################################################################################################################

# render Game Objects

player = Player(2 * tile_size, screen_height - 150)

malwareA_group = pygame.sprite.Group()
malwareB_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
bully_group = pygame.sprite.Group()

coin_group = pygame.sprite.Group()
lives_group = pygame.sprite.Group()
antivirus_group = pygame.sprite.Group()

exit_group = pygame.sprite.Group()
good_portals = pygame.sprite.Group()
good_o_portals = pygame.sprite.Group()
bad_portals = pygame.sprite.Group()
report_group = pygame.sprite.Group()
acp_group = pygame.sprite.Group()
bcp_group = pygame.sprite.Group()

# score coin
score_coin = Coin(screen_width - 3 * tile_size + 8, 2 * tile_size + tile_size//3 - 2)
scorecoin_group = pygame.sprite.Group()
scorecoin_group.add(score_coin)


# load in level data

if path.exists(f'levels/level{level}_data'):
    pickle_in = open(f'levels/level{level}_data', 'rb')
    world_data = pickle.load(pickle_in)

world = World(world_data)

##################################################################################################################
## buttons ##
##################################################################################################################

acp_exit_img = pygame.transform.scale(exit_image, (2 * tile_size, tile_size))

restart_button = Button(14 * tile_size, screen_height // 2 + 60, restart_image)
start_button = Button(tile_size * 12, screen_height // 2 + tile_size, start_image)
exit_button = Button(screen_width - tile_size * 16, screen_height // 2 + tile_size, exit_image)
done_button = Button(20 * tile_size, 8 * tile_size, done_btn_img)
done_button_2 = Button(26 * tile_size, 8 * tile_size, done_btn_img)

download_button = Button(20 * tile_size, 12 * tile_size, dwnld_img)
password_button = Button(20 * tile_size, 10 * tile_size, pwd_btn_img)
acp_exit_button = Button(20 * tile_size, 14 * tile_size, acp_exit_img)

buy_life_button = Button(20 * tile_size, 10 * tile_size, buy_life_img)
buy_av_button = Button(20 * tile_size, 12 * tile_size, buy_av_img)

#*****************************************************************************************************************

# Mini Game vars



width, height = (400, 600)
offset = 100
road_w = int(width)
roadmark_w = int(width/80)

instructionsA = "Dodge the offensive messages using the"
instructionsB = "LEFT and RIGHT arrows keys to"
instructionsC = "successfully report the bully"


lane1 = int(road_w/8) + offset
lane2 = int(3 * road_w/8) + offset
lane3 = int(5 * road_w/8) + offset
lane4 = int(7 * road_w/8) + offset

speed = 4

mini_game_over = 0
player_coords = lane2, height*0.9
msgA_coords = lane3, height*0.1
msgB_coords = lane1, height*0.1 - 330


#car = Player_2(lane2, height*0.9)
#car2 = MessageA(lane3, height*0.1)
#car3 = MessageB(lane1, height*0.1)

# load player vehicle
car = pygame.image.load("images/guy1.png")
car = pygame.transform.scale(car, (80, 125))
car_rect = car.get_rect()
car_rect.center = player_coords

# load enemy vehicle
car2 = pygame.image.load("images/message.jpg")
car2 = pygame.transform.scale(car2, (100 - roadmark_w - 2, 50))
car2_rect = car2.get_rect()
car2_rect.center = msgA_coords

car3 = pygame.image.load("images/message.jpg")
car3 = pygame.transform.scale(car3, (100 - roadmark_w - 2, 50))
car3_rect = car3.get_rect()
car3_rect.center = msgB_coords

counter = 0
curr_lane = 2
max_lanes = 4




##################################################################################################################
##___##  Game Loop  ##___##
###################################################################################################################
run = True

while run:

    clock.tick(fps)

    screen.blit(bg_full_img, (0,0))
    #screen.blit(sun_img, (100, 50))

    #draw_grid()

    if main_menu:
        draw_text("Into the Multiwebs", fontA, white, 14 * tile_size, 5 * tile_size)


        if exit_button.draw():
            run = False
        if start_button.draw():
            main_menu = False

    elif access_pt:
        draw_text("Access Point", fontA, white, 14 * tile_size, 4 * tile_size)
        draw_text("Game saved", font_tutorial, green, 14 * tile_size, 6 * tile_size)
        draw_text("Continue?", font_tutorial, white, 14 * tile_size, 8 * tile_size + tile_size//2)
        draw_text("Exit Game?", font_tutorial, white, 14 * tile_size, 14 * tile_size + tile_size//2)

        scorecoin_group.draw(screen)
        draw_text('Lives: ' + str(lives), font_score, white, screen_width - 3 * tile_size, tile_size + tile_size // 3)
        draw_text('x ' + str(score), font_score, white, screen_width - 3 * tile_size + 20 ,2 * tile_size + 3)

        draw_text("Downlaods", font_tutorial, white, 14 * tile_size, 12 * tile_size + tile_size//2)
        draw_text("Change Password", font_tutorial, white, 14 * tile_size, 10 * tile_size + tile_size//2)

        if malware:
            draw_text('You are infected with Malware!! :(', font_score, green, int(1.5 * tile_size), 2 * tile_size)
            draw_text('Malware: Infected', font_score, red, int(1.5 * tile_size), 10 + tile_size)
        else:
            draw_text('Malware: None', font_score, grey, int(1.5 * tile_size), 10 + tile_size)

        if download_button.draw():
            from_pause = 0
            download_menu = True
            access_pt = False
            
        if password_button.draw():
            print("Click")

        if done_button.draw():
            access_pt = False
        if acp_exit_button.draw():
            run = False
     
    
    elif pause_menu:
        draw_text("Well done", fontA, white, 14 * tile_size, 4 * tile_size)
        draw_text("Level Complete!!!", font_tutorial, green, 14 * tile_size, 6 * tile_size)
        draw_text("Continue?", font_tutorial, white, 14 * tile_size, 8 * tile_size + tile_size//2)
        draw_text("Exit Game?", font_tutorial, white, 14 * tile_size, 14 * tile_size + tile_size//2)

        scorecoin_group.draw(screen)
        draw_text('Lives: ' + str(lives), font_score, white, screen_width - 3 * tile_size, tile_size + tile_size // 3)
        draw_text('x ' + str(score), font_score, white, screen_width - 3 * tile_size + 20 ,2 * tile_size + 3)

        draw_text("Downloads", font_tutorial, white, 14 * tile_size, 12 * tile_size + tile_size//2)
        draw_text("Change Password", font_tutorial, white, 14 * tile_size, 10 * tile_size + tile_size//2)

        if malware:
            draw_text('You are infected with Malware!! :(', font_score, green, int(1.5 * tile_size), 2 * tile_size)
            draw_text('Malware: Infected', font_score, red, int(1.5 * tile_size), 10 + tile_size)
        else:
            draw_text('Malware: None', font_score, grey, int(1.5 * tile_size), 10 + tile_size)

        if download_button.draw():
            from_pause = 1
            download_menu = True
            pause_menu = False
            print("click")
        if password_button.draw():
            print("Click")

        if done_button.draw():
            pause_menu = False
        if acp_exit_button.draw():
            run = False
            

    elif download_menu:
        draw_text("Downloads", fontA, white, 14 * tile_size, 4 * tile_size)
        draw_text("Continue?", font_tutorial, white, 14 * tile_size, 8 * tile_size + tile_size//2)
        draw_text("Extra life", font_tutorial, white, 14 * tile_size, 10 * tile_size + tile_size//2)
        draw_text("Antivirus", font_tutorial, white, 14 * tile_size, 12 * tile_size + tile_size//2)

        scorecoin_group.draw(screen)
        draw_text('Lives: ' + str(lives), font_score, white, screen_width - 3 * tile_size, tile_size + tile_size // 3)
        draw_text('x ' + str(score), font_score, white, screen_width - 3 * tile_size + 20 ,2 * tile_size + 3)

        if malware:
            draw_text('You are infected with Malware!! :(', font_score, green, int(1.5 * tile_size), 2 * tile_size)
            draw_text('Malware: Infected', font_score, red, int(1.5 * tile_size), 10 + tile_size)
        else:
            draw_text('Malware: None', font_score, grey, int(1.5 * tile_size), 10 + tile_size)

        if done_button.draw():
            if from_pause == 1:
                download_menu = False
                pause_menu = True
            elif from_pause == 0:
                download_menu = False
                access_pt = True
        if buy_life_button.draw():
            if score < 9:
                draw_text("Insufficient coins", font_tutorial, red, 14 * tile_size, 6 * tile_size)
            elif score >= 9:
                lives += 1
                score -= 9
        if buy_av_button.draw():
            if score < 9:
                draw_text("Insufficient coins", font_tutorial, red, 14 * tile_size, 6 * tile_size)
            elif score >= 9:
                if not malware:
                    pass
                elif malware:
                    malware = False
                    score -= 9
            

    elif mini_game:
        draw_text(instructionsA, font_tutorial, grey, 20 * tile_size, 4 * tile_size)
        draw_text(instructionsB, font_tutorial, grey, 20 * tile_size, 5 * tile_size)
        draw_text(instructionsC, font_tutorial, grey, 20 * tile_size, 6 * tile_size)

        draw_text("Skip? Cost = 50c", font_tutorial, grey, 20 * tile_size, 8 * tile_size + tile_size // 2)
        if done_button_2.draw():
            if score < 30:
                draw_text("Insufficeint coins", font_tutorial, red, 20 * tile_size, 9 * tile_size)
                
            if score >= 30:
                mini_game = False
                score -= 30
                player.reset(bully_port[0][0], bully_port[0][1])

        rt = 0
        if mini_game_over == 0:
            
            counter += 1
            if counter == 1000:
                mini_game_over = 1
                print("You win", speed)
            # animate enemy vehicle

            car2_rect.y += speed
            car3_rect.y += speed
            #car2.move()

            if car2_rect.y > height:
                num = random.randint(0,300)
                new_lane = num % 4
                if  new_lane == 0:
                    car2_rect.center = lane1, -100
                elif new_lane == 1:
                    car2_rect.center = lane2, -100
                elif new_lane == 2:
                    car2_rect.center = lane3, -100
                else:
                    car2_rect.center = lane4, -100


            if car3_rect.y > height:
                num = random.randint(0,300)
                new_lane = num % 4
                if  new_lane == 0:
                    car3_rect.center = lane1, -100
                elif new_lane == 1:
                    car3_rect.center = lane2, -100
                elif new_lane == 2:
                    car3_rect.center = lane3, -100
                else:
                    car3_rect.center = lane4, -100

            # end game
            if car_rect[0] == car2_rect[0] and car2_rect[1] > car_rect[1] - 87:
                print("GAME OVER! YOU LOST")
                mini_game_over = -1
            if car_rect[0] == car3_rect[0] and car3_rect[1] > car_rect[1] - 87:
                print("GAME OVER! YOU LOST")
                mini_game_over = -1


            # event listeners
            for event in pygame.event.get():
                if event.type == QUIT:
                    mini_game = False
                if event.type == KEYDOWN:
                    if event.key in [K_a, K_LEFT]:
                        if curr_lane > 0:
                            car_rect.x -= int(road_w/4)
                            #car_loc = car_loc.move([-int(road_w/4), 0])
                            curr_lane -= 1
                        else:
                            pass
                    if event.key in [K_d, K_RIGHT]:
                        if curr_lane <= max_lanes:
                            car_rect.x += int(road_w/4)
                            #car_loc = car_loc.move([int(road_w/4), 0])
                            curr_lane += 1

        # centre line
        pygame.draw.rect(screen, (0, 240, 0), (width/2 - roadmark_w/2 + offset, 0, roadmark_w, height))

        pygame.draw.rect(screen, (0, 240, 0), (width/4 - roadmark_w/4 + offset, 0, roadmark_w, height))

        pygame.draw.rect(screen, (0, 240, 0), (3 * width/4 - roadmark_w/4 + offset, 0, roadmark_w, height))

        pygame.draw.rect(screen, (255, 0, 0), (width/2 - road_w/2 - roadmark_w*3 + offset - roadmark_w, 0, roadmark_w * 2, height))

        # right line
        pygame.draw.rect(screen, (255, 0, 0), (width/2 + road_w/2 - roadmark_w*3 + offset + roadmark_w, 0, roadmark_w * 2, height))

        screen.blit(car, car_rect)
        screen.blit(car2, car2_rect)
        screen.blit(car3, car3_rect)
        

        if mini_game_over == -1:
            time.sleep(1)
            print("clicked")
            car.rect.center = player_coords
            car2.rect.center = msgA_coords
            car3.rect.center = msgB_coords
            mini_game_over = 0
        
        if mini_game_over == 1:
            while rt < 50:
                clock.tick(fps)
                #car2_loc[1] -= speed
                #car3_loc[1] -= speed
                rt += 1
            
                mini_game = False
                report_group.empty()
                mini_game = False
                bully_beat = True
                checkpoint = [bully_port[0][0], bully_port[0][1]]
                player.reset(bully_port[0][0], bully_port[0][1])


    elif bully_beat:
        draw_text("Success!!", fontA, white, 14 * tile_size, 4 * tile_size)
        draw_text("100 coins awarded", font_tutorial, green, 14 * tile_size, 6 * tile_size)
        draw_text("Continue?", font_tutorial, white, 14 * tile_size, 8 * tile_size + tile_size//2)

        if done_button.draw():
            bully_beat = False
            score += 100
            
        

    elif win_menu:
        draw_text("You Win!!", fontA, green, 14 * tile_size, 6 * tile_size)
        draw_text("Score    " + str(score), font_tutorial, white, 14 * tile_size, 8 * tile_size)
        


        # restart game

        if restart_button.draw():
            level = 1
            world_data = []
            world = reset_level(level)
            game_over = 0
            score = 0
            malware = False
            win_menu = False
        

    elif loss_menu:
        draw_text("You Lose :(", fontA, red, 14 * tile_size, 6 * tile_size)
        draw_text("Score    " + str(score), font_tutorial, white, 14 * tile_size, 8 * tile_size)
        

        # restart game

        if restart_button.draw():
            level = 1
            lives = 3
            world_data = []
            world = reset_level(level)
            game_over = 0
            score = 0
            malware = False
            loss_menu = False
        

    else:
        world.draw()

        if game_over == 0:

            malwareA_group.update()
            malwareB_group.update()
            platform_group.update()
            # update score
            # check coin collection
            if pygame.sprite.spritecollide(player, coin_group, True):
                coin_fx.play()
                score += 1

            draw_text('Lives: ' + str(lives), font_score, white, screen_width - 3 * tile_size, tile_size + tile_size // 3)
            draw_text('x ' + str(score), font_score, white, screen_width - 3 * tile_size + 20 , 2 * tile_size + 3)
            

            level_text(level)

            if malware:
                draw_text('You are infected with Malware!! :(', font_score, green, int(1.5 * tile_size), 2 * tile_size)
                draw_text('Malware: Infected', font_score, red, int(1.5 * tile_size), tile_size + 10)
            else:
                draw_text('Malware: None', font_score, grey, int(1.5 * tile_size), tile_size + 10)
        

        malwareA_group.draw(screen)
        malwareB_group.draw(screen)
        lava_group.draw(screen)
        coin_group.draw(screen)
        exit_group.draw(screen)
        good_portals.draw(screen)
        good_o_portals.draw(screen)
        bad_portals.draw(screen)
        report_group.draw(screen)
        lives_group.draw(screen)
        antivirus_group.draw(screen)
        scorecoin_group.draw(screen)
        acp_group.draw(screen)
        bcp_group.draw(screen)
        platform_group.draw(screen)
        bully_group.draw(screen)

        game_over = player.update(game_over)

        # player has died
        if game_over == -1:
            if has_lives(lives):
                time.sleep(0.2)
                world_data = []
                world = reset_level(level)
                game_over = 0
                lives -= 1
            else:
                loss_menu = True
                


        if game_over == 1:
            # reset game go to next level
            level += 1
            if level <= max_levels:
                pause_menu = True
                world_data = []
                check_point = [2 * tile_size, screen_height - 150]
                world = reset_level(level)
                game_over = 0
            else:
                win_menu = True
                    

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()




# Menus

### Pwd menu

## Set Password
## Random string generator

## more SFX

# levels


# .exe conversion
# Documentation
# Demo
