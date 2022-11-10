import pygame, sys
import pygame_menu
import datetime
import time

from settings import * 
from level import Level, Difficulies
from db import Connector

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption('Bill\'s Revenge')
clock = pygame.time.Clock()

menu_song = pygame.mixer.Sound(IN_MENU_SONG)
pygame.mixer.Sound.play(menu_song)

con = Connector()

nb_ennemies = 1
difficulty = Difficulies.PEACEFUL

def set_nb_ennemies(_, value):
	global nb_ennemies # TODO: CHANGE IT!!
	nb_ennemies = value

def set_difficulty(_, value):
	global difficulty # TODO: CHANGE IT!!
	difficulty = value

def run_game(table: pygame_menu.widgets.Table):
	menu_song.fadeout(100)
	level = Level(nb_ennemies, difficulty)
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

# Score Menu
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

# Difficulty Menu
difficulty_menu = pygame_menu.Menu('Difficulty', SCREEN_WIDTH, SCREEN_HEIGHT,
                       theme=mytheme)
difficulty_menu.add.selector('Steve\'s humour:',
	[('Peaceful', Difficulies.PEACEFUL), ('Aggressive', Difficulies.AGGRESSIVE)], 
	onchange=set_difficulty)
difficulty_menu.add.selector('Nb of ennemies:',
	[ (f'{i}', i) for i in range(1, MAX_NB_ENNEMY+1) ],
	onchange=set_nb_ennemies)
difficulty_menu.add.button('Go back to menu', pygame_menu.events.BACK)


menu.add.button('Play', run_game, table)
menu.add.button('Difficulty', difficulty_menu)
menu.add.button('Scores', score_menu)
menu.add.button('Quit', pygame_menu.events.EXIT)

menu.mainloop(screen)