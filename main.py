import pygame, sys
import pygame_menu
import datetime
import time

from settings import * 
from level import Level
from db import Connector

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption('Bill\'s Revenge')
clock = pygame.time.Clock()

menu_song = pygame.mixer.Sound(IN_MENU_SONG)
pygame.mixer.Sound.play(menu_song)

con = Connector()

def run_game(table: pygame_menu.widgets.Table):
	menu_song.fadeout(100)
	level = Level()
	start_time = time.time()

	while not level.is_finished():
		# event loop
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
		
		level.run()

		# drawing logic
		pygame.display.update()
		clock.tick(60)

	level.quit()

	res = level.scores()

	date = datetime.datetime.now()
	date_str = f'{date.day}/{date.month}/{date.year}'

	con.add(date_str, str(res['score']), str(round(time.time() - start_time,2)))
	table.add_row([ date_str, str(res['score']), str(round(time.time() - start_time,2)) ])
	pygame.mixer.Sound.play(menu_song)

mytheme = pygame_menu.themes.THEME_DEFAULT.copy()
myimage = pygame_menu.baseimage.BaseImage(
    image_path=MENU,
    drawing_mode=pygame_menu.baseimage.IMAGE_MODE_REPEAT_XY,
)
myimage.resize(SCREEN_WIDTH,SCREEN_HEIGHT)
mytheme.background_color = myimage

menu = pygame_menu.Menu('Bill\'s Revenge', SCREEN_WIDTH, SCREEN_HEIGHT,
                       theme=mytheme)

score_menu = pygame_menu.Menu('Scores', SCREEN_WIDTH, SCREEN_HEIGHT,
                       theme=mytheme)
table = score_menu.add.table(table_id='Score table')
table.default_cell_padding = 20
table.add_row(['DATE', 'SCORE', 'TIME'],
              cell_font=pygame_menu.font.FONT_OPEN_SANS_BOLD,
			  cell_align=pygame_menu.locals.ALIGN_CENTER)
for score in con.get_stats():
	table.add_row(score, cell_align=pygame_menu.locals.ALIGN_CENTER)
score_menu.add.button('Go back to menu', pygame_menu.events.BACK)

menu.add.button('Play', run_game, table)
menu.add.button('Scores', score_menu)
menu.add.button('Quit', pygame_menu.events.EXIT)

menu.mainloop(screen)