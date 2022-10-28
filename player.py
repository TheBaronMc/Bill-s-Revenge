import pygame
from typing import Tuple

from settings import BILL_GATES, PLAYER_HEIGHT, PLAYER_WIDTH

class Player(pygame.sprite.Sprite):
    def __init__(self, image: str, size: Tuple[int, int], *groups: pygame.sprite.AbstractGroup) -> None:
        super().__init__(*groups)

        surface = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(surface, size)
        self.rect = self.image.get_rect()


class BillGates(Player):
    def __init__(self, *groups: pygame.sprite.AbstractGroup) -> None:
        super().__init__(BILL_GATES, (PLAYER_WIDTH, PLAYER_HEIGHT), *groups)
