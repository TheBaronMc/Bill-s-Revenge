import pygame
import random
import enum

from typing import Dict, List, Union, Sequence, Any

from player import BillGates, PlayableSurface, Character, SteveJobs
from settings import *

class Difficulies(enum.Enum):
    PEACEFUL = enum.auto()
    AGGRESSIVE = enum.auto()

class Level():
    def __init__(self, nb_ennemies: int, difficulty: Difficulies):

        # Level setup
        self.display_surface = pygame.display.get_surface()
        
        # sprite group setup
        self.visible_sprites = CameraGroup()
        self.active_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()
        self.ennemy_sprites = pygame.sprite.Group()

        self.in_game_song = pygame.mixer.Sound(IN_GAME_SONG)
        self.in_game_song.set_volume(0.2)

        self.nb_ennemies = nb_ennemies
        self.difficulty = difficulty

        self.setup_level()

    def setup_level(self):

        # charging background
        self.background = Background([self.visible_sprites])
        self.player = BillGates([self.visible_sprites, self.active_sprites])
        self.player.rect.bottomleft = self.display_surface.get_rect().bottomleft

        game_surface = PlayableSurface((PLAYABLE_SURFACE_WIDTH, PLAYABLE_SURFACE_HEIGHT))
        self.player.set_playable_surface(game_surface)

        ennemy_aggressive = self.difficulty == Difficulies.AGGRESSIVE
        for _ in range(self.nb_ennemies):
            x = random.randint(200, PLAYABLE_SURFACE_WIDTH-PLAYER_WIDTH)
            offset_y = random.randint(0, PLAYABLE_SURFACE_HEIGHT)
            ennemy = SteveJobs(ennemy_aggressive, (x, SCREEN_HEIGHT - offset_y), [self.active_sprites, self.visible_sprites, self.ennemy_sprites])
            ennemy.add_ennemies(self.player)
            ennemy.set_playable_surface(game_surface)
            self.player.add_ennemies(ennemy)

        self.score_board = ScoreBoard(self.player, [self.active_sprites, self.visible_sprites])
        self.health_view = HealthView(self.player, [self.active_sprites, self.visible_sprites])

        # start music
        pygame.mixer.Sound.play(self.in_game_song)

    def run(self):
        self.active_sprites.update()
        self.visible_sprites.custom_draw(self.player, self.background, self.score_board, self.health_view)

    def is_finished(self) -> bool:
        return len(self.ennemy_sprites.sprites()) == 0 or self.player.is_dead()

    def scores(self) -> Dict:
        return { 
            'score': self.player.get_score(), 
            'gameover': self.player.is_dead(), 
            'aggressive': self.difficulty == Difficulies.AGGRESSIVE,
            'nb_ennemies': self.nb_ennemies
            }
    
    def quit(self):
        pygame.mixer.Sound.stop(self.in_game_song)


class Background(pygame.sprite.Sprite):
    def __init__(self, *groups: pygame.sprite.AbstractGroup) -> None:
        super().__init__(*groups)

        surface = pygame.image.load(BACKGROUND).convert()
        self.image = pygame.transform.scale(surface, (BACKGROUND_WIDTH, BACKGROUND_HEIGHT))
        self.rect = self.image.get_rect()


class CameraGroup(pygame.sprite.Group):
    def __init__(self, *sprites: Union[pygame.sprite.Sprite, Sequence[pygame.sprite.Sprite]]) -> None:
        super().__init__(*sprites)

        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

        # camera
        self.camera_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

    def custom_draw(self, player: BillGates, background: Background = None, score_board = None, health_view = None):

        # Camera position
        half_w = SCREEN_WIDTH // 2
        if background.rect.left + player.rect.centerx < half_w:
            self.camera_rect.centerx = half_w
        elif background.rect.right - player.rect.centerx < half_w:
            self.camera_rect.centerx = background.rect.right - half_w
        else:
            self.camera_rect.centerx = player.rect.centerx

        # camera offset 
        self.offset = pygame.math.Vector2(self.camera_rect.left, 0)

        # update score board position
        if score_board:
            score_board.rect.topleft = self.camera_rect.topleft
        if health_view:
            health_view.rect.topleft = self.camera_rect.topright
            health_view.rect.left -= health_view.rect.width
        
        # Display all sprites
        player_sprites: List[Character] = []
        for sprite in self.sprites():
            offset_pos = sprite.rect.topleft - self.offset

            if not isinstance(sprite, Character):
                self.display_surface.blit(sprite.image, offset_pos)
            else:
                player_sprites.append(sprite)

        player_sprites.sort(key=lambda player: player.rect.bottom)
        for player_sprite in player_sprites:
            offset_pos = player_sprite.rect.topleft - self.offset
            self.display_surface.blit(player_sprite.image, offset_pos)


class ScoreBoard(pygame.sprite.Sprite):
    def __init__(self, player: Character, *groups: pygame.sprite.AbstractGroup) -> None:
        super().__init__(*groups)

        self.font = pygame.font.SysFont(None, 72)
        self.image = self.font.render('SCORE: 000000', True, (255,255,0))
        self.rect = self.image.get_rect()
        self.player = player

    def update(self, *args: Any, **kwargs: Any) -> None:
        super().update(*args, **kwargs)
        self.image = self.font.render('SCORE: {:0>6}'.format(self.player.get_score()), True, (255,255,0))

        self.screen = pygame.display.get_surface()
        self.rect.left = self.screen.get_rect().left

class HealthView(pygame.sprite.Sprite):
    def __init__(self, player: Character, *groups: pygame.sprite.AbstractGroup) -> None:
        super().__init__(*groups)

        self.player = player
        self.font = pygame.font.SysFont(None, 72)
        self.image = self.font.render('HP: 000', True, (255,0,0))
        self.rect = self.image.get_rect()

    def update(self, *args: Any, **kwargs: Any) -> None:
        super().update(*args, **kwargs)
        self.image = self.font.render('HP: {:0>3}'.format(self.player.health), True, (255,0,0))

        self.screen = pygame.display.get_surface()
        self.rect.left = self.screen.get_rect().right - self.rect.width