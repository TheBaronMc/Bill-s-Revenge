import pygame
from player import BillGates, PlayableSurface
from settings import *

class Level():
    def __init__(self):
        
        # Level setup
        self.display_surface = pygame.display.get_surface()
        
        # sprite group setup
        self.visible_sprites = pygame.sprite.Group()
        self.active_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()

        self.in_game_song = pygame.mixer.Sound(IN_GAME_SONG)
        self.in_game_song.set_volume(0.2)

        self.setup_level()

    def setup_level(self):

        # charging background
        self.Background([self.visible_sprites])
        bg = BillGates(5, [self.visible_sprites, self.active_sprites])
        bg.rect.bottomleft = self.display_surface.get_rect().bottomleft
        bg.set_playable_surface(PlayableSurface((PLAYABLE_SURFACE_WIDTH, PLAYABLE_SURFACE_HEIGHT)))

        # start music
        pygame.mixer.Sound.play(self.in_game_song)

    def run(self):
        self.active_sprites.update()
        self.visible_sprites.draw(self.display_surface)


    class Background(pygame.sprite.Sprite):
        def __init__(self, *groups: pygame.sprite.AbstractGroup) -> None:
            super().__init__(*groups)

            surface = pygame.image.load(BACKGROUND).convert()
            self.image = pygame.transform.scale(surface, (BACKGROUND_WIDTH, BACKGROUND_HEIGHT))
            self.rect = self.image.get_rect()
