import pygame
import random

from typing import Union, Sequence

from player import BillGates, PlayableSurface, SteveJobs
from settings import *

class Level():
    def __init__(self):
        
        # Level setup
        self.display_surface = pygame.display.get_surface()
        
        # sprite group setup
        self.visible_sprites = CameraGroup()
        self.active_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()

        self.in_game_song = pygame.mixer.Sound(IN_GAME_SONG)
        self.in_game_song.set_volume(0.2)

        self.setup_level()

    def setup_level(self):

        # charging background
        self.background = Background([self.visible_sprites])
        self.player = BillGates(5, [self.visible_sprites, self.active_sprites])
        self.player.rect.bottomleft = self.display_surface.get_rect().bottomleft
        self.player.set_playable_surface(PlayableSurface((PLAYABLE_SURFACE_WIDTH, PLAYABLE_SURFACE_HEIGHT)))
        for _ in range(NB_ENNEMY):
            offset_x = random.randint(200, PLAYABLE_SURFACE_WIDTH)
            offset_y = random.randint(0, PLAYABLE_SURFACE_HEIGHT)
            self.player.add_ennemy(SteveJobs((offset_x, SCREEN_HEIGHT - offset_y), [self.visible_sprites]))

        # start music
        pygame.mixer.Sound.play(self.in_game_song)

    def run(self):
        self.active_sprites.update()
        self.visible_sprites.custom_draw(self.player, self.background)


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

    def custom_draw(self, player: BillGates, background: Background = None):

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
        
        # Display all sprites
        for sprite in self.sprites():
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)        
