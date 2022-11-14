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

mytheme = pygame_menu.themes.THEME_DEFAULT.copy()
myimage = pygame_menu.baseimage.BaseImage(
    image_path=MENU,
    drawing_mode=pygame_menu.baseimage.IMAGE_MODE_REPEAT_XY,
)
myimage.resize(SCREEN_WIDTH,SCREEN_HEIGHT)
mytheme.background_color = myimage


class DataStore():
	def __init__(self) -> None:
		self.difficulty = Difficulies.PEACEFUL
		self.ennemies = 1

	def get_ennemies(self) -> int:
		return self.ennemies

	def get_difficulty(self) -> Difficulies:
		return self.difficulty

	def set_difficulty(self, d: Difficulies):
		self.difficulty = d

	def set_ennmies(self, e: int):
		self.ennemies = e 


class ScoreMenu(pygame_menu.Menu):
	def __init__(self):
		super().__init__('Scores', SCREEN_WIDTH, SCREEN_HEIGHT, theme=mytheme)

		self.table = self.add.table(table_id='Score table')
		self.table.default_cell_padding = 20
		self.table.add_row(['DATE', 'SCORE', 'NB_ENNEMIES', 'AGGRESSIVE', 'GAMEOVER','TIME'],
              cell_font=pygame_menu.font.FONT_OPEN_SANS_BOLD,
			  cell_align=pygame_menu.locals.ALIGN_CENTER)

		self.add.button('Refresh', self.refresh)
		self.add.button('Go back to menu', pygame_menu.events.BACK)

		self.rows = []

		self.refresh()

	def refresh(self):
		for row in self.rows:
			self.table.remove_row(row)

		self.rows = []

		for score in con.get_stats():
			self.rows.append(self.table.add_row(score, cell_align=pygame_menu.locals.ALIGN_CENTER))


class DifficultyMenu(pygame_menu.Menu):
	def __init__(self, ds: DataStore):
		super().__init__('Difficulty', SCREEN_WIDTH, SCREEN_HEIGHT, theme=mytheme)
		
		self.ds = ds
		self.add.selector('Steve\'s humour:',
			[('Peaceful', Difficulies.PEACEFUL), ('Aggressive', Difficulies.AGGRESSIVE)], 
			onchange=self.__set_difficulty)
		self.add.selector('Nb of ennemies:',
			[ (f'{i}', i) for i in range(1, MAX_NB_ENNEMY+1) ],
			onchange=self.__set_ennemies)
		self.add.button('Go back to menu', pygame_menu.events.BACK)

	def __set_difficulty(self, _, difficulty: Difficulies):
		self.ds.set_difficulty(difficulty)

	def __set_ennemies(self, _, ennemies: int):
		self.ds.set_ennmies(ennemies)


class GameRunner():
	def __init__(self, ds: DataStore) -> None:
		self.ds = ds

	def run(self):
		menu_song.fadeout(100)
		level = Level(self.ds.get_ennemies(), self.ds.get_difficulty())
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

		# end screen
		self.EndScreen(not res['gameover'])

		date = datetime.datetime.now()
		date_str = f'{date.day}/{date.month}/{date.year}'

		con.add(date_str, str(res['score']), str(res['nb_ennemies']), str(res['aggressive']), str(res['gameover']), str(round(time.time() - start_time,2)))
		pygame.mixer.Sound.play(menu_song)
	
	class EndScreen():
		def __init__(self, win: bool) -> None:
			window = pygame.sprite.Sprite()
			window.rect = pygame.rect.Rect(0,0,SCREEN_WIDTH,SCREEN_HEIGHT)
			screen = pygame.display.get_surface()

			window.rect.topleft = screen.get_rect().topleft
			window.image = pygame.surface.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
			window.image.fill((0,0,0))
			window.image.set_alpha(0)

			for i in range(0,100):
				screen.blit(window.image, window.rect)
				window.image.set_alpha(i)
				pygame.display.update()
			

			window.image.set_alpha(255)
			screen.blit(window.image, window.rect)
			pygame.display.update()

			message = pygame.sprite.Sprite()
			mesage_font = pygame.font.SysFont(None, 72)
			if win:
				message.image = mesage_font.render('WIN', True, (255,255,0))
			else:
				message.image = mesage_font.render('GAME OVER', True, (255,0,0))
			message.rect = message.image.get_rect()
			message.rect.centerx = screen.get_rect().centerx
			message.rect.bottom = screen.get_rect().centery - message.rect.height
			screen.blit(message.image, message.rect)

			keymessage = pygame.sprite.Sprite()
			key_mesage_font = pygame.font.SysFont(None, 32)
			if win:
				keymessage.image = key_mesage_font.render('Press any key', True, (255,255,0))
			else:
				keymessage.image = key_mesage_font.render('Press any key', True, (255,0,0))
			keymessage.rect = keymessage.image.get_rect()
			keymessage.rect.centerx = screen.get_rect().centerx
			keymessage.rect.bottom = screen.get_rect().centery + message.rect.height*2
			screen.blit(keymessage.image, keymessage.rect)

			pygame.display.update()
			
			level_quit = False
			while not level_quit:
				for event in pygame.event.get():
					if event.type == pygame.KEYDOWN:
						level_quit = True


menu = pygame_menu.Menu('Bill\'s Revenge', SCREEN_WIDTH, SCREEN_HEIGHT,
                       theme=mytheme)

data_store = DataStore()

score_menu = ScoreMenu()
difficulty_menu = DifficultyMenu(data_store)
game_runner = GameRunner(data_store)


menu.add.button('Play', game_runner.run)
menu.add.button('Difficulty', difficulty_menu)
menu.add.button('Scores', score_menu)
menu.add.button('Quit', pygame_menu.events.EXIT)

menu.mainloop(screen)

