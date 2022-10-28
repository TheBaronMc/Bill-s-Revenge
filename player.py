import pygame
from typing import Dict, Tuple

from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, image: str, size: Tuple[int, int], *groups: pygame.sprite.AbstractGroup) -> None:
        super().__init__(*groups)

        surface = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(surface, size)
        self.rect = self.image.get_rect()


class PlayableSurface(pygame.sprite.Sprite):
    def __init__(self, size: Tuple[int, int], *groups: pygame.sprite.AbstractGroup) -> None:
        super().__init__(*groups)

        self.image = pygame.Surface(size)
        #self.image.fill((0,0,255))
        self.rect = self.image.get_rect(topleft=(0, SCREEN_HEIGHT - size[1]))


class BillGates(Player):
    def __init__(self, speed: int, *groups: pygame.sprite.AbstractGroup) -> None:
        super().__init__(BILL_GATES_FRONT, (PLAYER_WIDTH, PLAYER_HEIGHT), *groups)

        self.movements: Dict[str,pygame.Surface] = {
            'STATIC': self.image,
            'DOWN': self.image,
            'UP': self.__load_image(BILL_GATES_BACK),
            'LEFT': self.__load_image(BILL_GATES_LEFT),
            'RIGHT': self.__load_image(BILL_GATES_RIGHT)
        }

        self.direction = pygame.math.Vector2()
        self.speed = speed

        self.playable_surface = None

    def set_playable_surface(self, surface: PlayableSurface):
        self.playable_surface = surface

    def update(self):
        self.__input()
        self.rect.center += self.direction * self.speed
        self.__playable_surface_collisions()

    def __input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_z]:
            self.direction.y = -1
            self.image = self.movements['UP']
        elif keys[pygame.K_s]:
            self.direction.y = 1
            self.image = self.movements['DOWN']
        else:
            self.direction.y = 0
            self.image = self.movements['STATIC']

        if keys[pygame.K_q]:
            self.direction.x = -1
            self.image = self.movements['LEFT']
        elif keys[pygame.K_d]:
            self.direction.x = 1
            self.image = self.movements['RIGHT']
        else:
            self.direction.x = 0

    def __playable_surface_collisions(self):
        if self.playable_surface:
            # check on x-axis
            if self.rect.bottom > self.playable_surface.rect.bottom:
                self.rect.bottom = self.playable_surface.rect.bottom

            if self.rect.bottom < self.playable_surface.rect.top:
                self.rect.bottom = self.playable_surface.rect.top

            # check on y-axis
            if self.rect.left < self.playable_surface.rect.left:
                self.rect.left = self.playable_surface.rect.left

            if self.rect.right > self.playable_surface.rect.right:
                self.rect.right = self.playable_surface.rect.right

    def __load_image(self, image: str) -> pygame.surface.Surface:
        surface = pygame.image.load(image).convert_alpha()
        return pygame.transform.scale(surface, (PLAYER_WIDTH, PLAYER_HEIGHT))
