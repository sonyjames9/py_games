import os
import random

import pygame

pygame.font.init()

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invader")

# Load images
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

# PLAYER SHIP
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))

YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# Background color
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))


# The laser implementation is such that when player moves the laser fired should not
# change direction. Fired laser should be independent of player or enemy movements
class Laser:
	def __init__(self, x, y, img):
		self.x = x
		self.y = y
		self.img = img
		# Mask is colliding with diff objects
		self.mask = pygame.mask.from_surface(self.img)
	
	def draw(self, window):
		window.blit(self.img, (self.x, self.y))
	
	# 	Laser movement
	def move(self, velocity):
		self.y += velocity
	
	def off_screen(self, height):
		return not (height > self.y >= 0)
	
	def collision(self, obj):
		return collide(self, obj)


class Ship:
	# This is an abstract class, where there are two ships
	# 1. Player ship
	# 2. Enemy ship
	# We will inherit from this class
	# Since both enemy and player ship will have some common properties,
	# so these properties can be shared
	COOLDOWN = 30
	
	def __init__(self, x, y, health=100):
		self.x = x
		self.y = y
		self.health = health
		self.ship_img = None
		self.laser_img = None
		self.lasers = []
		self.cool_down_counter = 0
	
	def draw(self, window):
		window.blit(self.ship_img, (self.x, self.y))
		# pygame.draw.rect(window, (255, 0, 0), (self.x, self.y, 50, 50), 2)
		for laser in self.lasers:
			laser.draw(window)
	
	# 2 methods of move_lasers is required
	# 1. to shoot player
	# 2, to shoot enemies
	def move_lasers(self, velocity, obj):
		self.cooldown()
		for laser in self.lasers:
			laser.move(velocity)
			if laser.off_screen(HEIGHT):
				self.lasers.remove(laser)
			elif laser.collision(obj):
				obj.health -= 10
				self.lasers.remove(laser)
	
	def get_width(self):
		return self.ship_img.get_width()
	
	def get_height(self):
		return self.ship_img.get_height()
	
	# handle cooldown counter
	def cooldown(self):
		if self.cool_down_counter >= self.COOLDOWN:
			self.cool_down_counter = 0
		elif self.cool_down_counter > 0:
			self.cool_down_counter += 1
	
	def shoot(self):
		if self.cool_down_counter == 0:
			laser = Laser(self.x, self.y, self.laser_img)
			self.lasers.append(laser)
			self.cool_down_counter = 1


class Player(Ship):
	def __init__(self, x, y, health=100):
		super().__init__(x, y, health)
		self.ship_img = YELLOW_SPACE_SHIP
		self.laser_img = YELLOW_LASER
		self.mask = pygame.mask.from_surface(self.ship_img)
		self.max_health = health
	
	def move_lasers(self, velocity, objs):
		self.cooldown()
		for laser in self.lasers:
			laser.move(velocity)
			if laser.off_screen(HEIGHT):
				self.lasers.remove(laser)
			else:
				for obj in objs:
					if laser.collision(obj):
						objs.remove(obj)
						# if laser in self.lasers:
						self.lasers.remove(laser)
						
	def draw(self, window):
		super().draw(window)
		self.health_bar(window)
	
	def health_bar(self, window):
		pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
		pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


class EnemyShip(Ship):
	# If the string color is matching the enemy ship, all the asset and functionality should point to same color.
	# If t
	COLOR_MAP = {
		"red": (RED_SPACE_SHIP, RED_LASER),
		"green": (GREEN_SPACE_SHIP, GREEN_LASER),
		"blue": (BLUE_SPACE_SHIP, BLUE_LASER),
	}
	
	def __init__(self, x, y, color, health=100):  # "red", "green", "blue"
		super().__init__(x, y, health)
		self.ship_img, self.laser_img = self.COLOR_MAP[color]
		self.mask = pygame.mask.from_surface(self.ship_img)
	
	def move(self, velocity):
		self.y += velocity
	
	def shoot(self):
		if self.cool_down_counter == 0:
			laser = Laser(self.x - 15, self.y, self.laser_img)
			self.lasers.append(laser)
			self.cool_down_counter = 1


# With the help of mask(pygame), we can find out of pixel of one image object has
# actually collided with second image object
def collide(obj1, obj2):
	offset_x = obj2.x - obj1.x
	offset_y = obj2.y - obj1.y
	return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None  # (x,y) is returned if True


def main():
	run = True
	FPS = 60
	level = 0
	lives = 5
	main_font = pygame.font.SysFont("comicsans", 20)
	lost_font = pygame.font.SysFont("comicsans", 30)
	
	enemies = []
	wave_length = 5
	enemy_velocity = 1
	player_velocity = 5
	laser_velocity = 5
	
	player = Player(300, 630)
	
	ship = Ship(300, 650)
	
	clock = pygame.time.Clock()
	
	lost = False
	lost_count = 0
	
	def redraw_window():
		WIN.blit(BG, (0, 0))
		# draw text
		# color codes - RGB
		lives_label = main_font.render(f" Lives: {lives}", True, (255, 255, 255))
		level_label = main_font.render(f" Level: {level}", True, (255, 255, 255))
		WIN.blit(lives_label, (10, 10))
		WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
		
		# For each enemy draw on the screen
		for enemy in enemies:
			enemy.draw(WIN)
		
		player.draw(WIN)
		
		if lost:
			lost_label = lost_font.render("You Lost!!", True, (255, 255, 255))
			WIN.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, 350))
		
		pygame.display.update()
	
	while run:
		clock.tick(FPS)
		redraw_window()
		
		# If lives is less than 0, display a message to restart/exit the game
		if lives <= 0 or player.health <= 0:
			lost = True
			lost_count += 1
		
		if lost:
			if lost_count > FPS * 5:
				run = False
			else:
				continue
		
		# If no more enemies are on screen, the list will be empty, the level will increment
		if len(enemies) == 0:
			level += 1
			wave_length += 5
			
			# create new 5 enemies, spawn new enemies and get them a level down
			# whenever level of the player increases by killing previous enemies
			for i in range(wave_length):
				enemy = EnemyShip(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
				enemies.append(enemy)
		
		# Below event will check 60 times/second, if user has clicked exit button.
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
		
		keys = pygame.key.get_pressed()
		if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and (player.x - player_velocity) > 0:  # left
			player.x -= player_velocity
		if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and (
			player.x + player_velocity + player.get_width()) < WIDTH:  # right
			player.x += player_velocity
		if (keys[pygame.K_w] or keys[pygame.K_UP]) and (player.y - player_velocity) > 0:  # up
			player.y -= player_velocity
		if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and (
			player.y + player_velocity + player.get_height() + 20) < HEIGHT:  # down
			player.y += player_velocity
		if keys[pygame.K_SPACE]:
			player.shoot()
		
		# Every enemy in enemy list is spawned and moves down until the screen, thereby reducing the lives of player by 1
		# OR player kills enemy before the enemy ship moves below the screen
		for enemy in enemies[:]:
			enemy.move(enemy_velocity)
			enemy.move_lasers(laser_velocity, player)
			
			if random.randrange(0, 4 * FPS) == 1:
				enemy.shoot()
			
			if collide(enemy, player):
				player.health -= 10
				enemies.remove(enemy)
			
			# If enemy goes beyond the screen height, player lives are lost by 1
			elif enemy.y + enemy.get_height() > HEIGHT:
				lives -= 1
				enemies.remove(enemy)
			# if lives < 0:
			# 	lives = 0
			# Remove enemy from enemies list
		
		player.move_lasers(-laser_velocity, enemies)


# If any mouse_button is pressed, restart the game from main() method
# If we press the close/exit button, then run will be false and game will exit
#
def main_menu():
	title_font = pygame.font.SysFont("comicsans", 50)
	run = True
	while run:
		WIN.blit(BG, (0, 0))
		title_label = title_font.render("Press the mouse to begin....", True, (255, 255, 255))
		WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
		pygame.display.update()
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
			if event.type == pygame.MOUSEBUTTONDOWN:
				main()
				
	pygame.quit()

main_menu()
