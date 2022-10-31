import pygame, sys
import pygame_menu

from settings import * 
from level import Level

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption('Bill\'s Revenge')
clock = pygame.time.Clock()

menu_song = pygame.mixer.Sound(IN_MENU_SONG)
pygame.mixer.Sound.play(menu_song)

def run_game():
	menu_song.fadeout(100)
	level = Level()

	while True:
		# event loop
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
		
		level.run()

		# drawing logic
		pygame.display.update()
		clock.tick(60)


menu = pygame_menu.Menu('Bill\'s Revenge', SCREEN_WIDTH, SCREEN_HEIGHT,
                       theme=pygame_menu.themes.THEME_BLUE)

menu.add.button('Play', run_game)
menu.add.button('Quit', pygame_menu.events.EXIT)

menu.mainloop(screen)