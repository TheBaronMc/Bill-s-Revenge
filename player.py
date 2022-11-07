import pygame
import time

from math import sqrt
from typing import Dict, Iterable, Tuple, Any

from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, image: str, size: Tuple[int, int], *groups: pygame.sprite.AbstractGroup) -> None:
        super().__init__(*groups)

        surface = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(surface, size)
        self.rect = self.image.get_rect()

        self.health = 100
        self.power = 50
        self.ennemies = []

        self.score = 0

    def add_ennemy(self, ennemy):
        self.ennemies.append(ennemy)

    def attack(self):
        hits = pygame.sprite.spritecollide(self, self.ennemies, False)
        for ennemy in hits:
            distance = sqrt((ennemy.rect.centerx - self.rect.centerx)**2 + (ennemy.rect.bottom - self.rect.bottom)**2)
            if distance <= (PLAYER_WIDTH / 3) * 2:
                ennemy.get_hit()
                self.score += 50
            

    def get_hit(self, damage: int = 50):
        self.health -= damage
        if self.health <= 0:
            self.die()

    def get_score(self) -> int:
        return self.score

    def die(self):
        self.kill()

    def is_dead(self) -> bool:
        return self.health <= 0


class PlayableSurface(pygame.sprite.Sprite):
    def __init__(self, size: Tuple[int, int], *groups: pygame.sprite.AbstractGroup) -> None:
        super().__init__(*groups)

        self.image = pygame.Surface(size)
        #self.image.fill((0,0,255))
        self.rect = self.image.get_rect(topleft=(0, SCREEN_HEIGHT - size[1]))


class SteveJobs(Player):
    def __init__(self, starting_position: Tuple[int,int], *groups: pygame.sprite.AbstractGroup) -> None:
        super().__init__(STEVE_JOBS, (PLAYER_WIDTH, PLAYER_HEIGHT), *groups)

        self.images: Dict[str,pygame.Surface] = {
            'NORMAL': self.image,
            'ATTACKED': self.__load_image(STEVE_JOBS_ATTACKED)
        }

        self.rect.bottomleft = starting_position
        self.cry = pygame.mixer.Sound(WILHELM)
        self.cry.set_volume(0.1)
        self.sound_played = False
        
        self.attacked = False
        self.attack_animation_duration = 0

    def get_hit(self, damage: int = 50):
        super().get_hit(damage)
        if not self.sound_played:
            pygame.mixer.Sound.play(self.cry)
            self.sound_played = True
            self.attacked = True
            self.attack_animation_duration = time.time()
            self.image = self.images['ATTACKED']
            
    def update(self, *args: Any, **kwargs: Any) -> None:
        super().update(*args, **kwargs)
        if self.attacked and (time.time() - self.attack_animation_duration > 0.5):
            self.image = self.images['NORMAL']
            self.attacked = False

    def __load_image(self, image: str) -> pygame.surface.Surface:
        surface = pygame.image.load(image).convert_alpha()
        return pygame.transform.scale(surface, (PLAYER_WIDTH, PLAYER_HEIGHT))


class BillGates(Player):
    def __init__(self, speed: int, *groups: pygame.sprite.AbstractGroup) -> None:
        super().__init__(BILL_GATES_FRONT, (PLAYER_WIDTH, PLAYER_HEIGHT), *groups)

        self.movements: Dict[str,pygame.Surface] = {
            'STATIC': self.image,
            'DOWN': self.image,
            'UP': self.__load_image(BILL_GATES_BACK),
            'LEFT': self.__load_image(BILL_GATES_LEFT),
            'RIGHT': self.__load_image(BILL_GATES_RIGHT),
            'STATIC_ATTACK': self.__load_image(BILL_GATES_FRONT_ATTACK),
            'DOWN_ATTACK': self.__load_image(BILL_GATES_FRONT_ATTACK),
            'UP_ATTACK':  self.__load_image(BILL_GATES_BACK_ATTACK),
            'LEFT_ATTACK':  self.__load_image(BILL_GATES_LEFT_ATTACK),
            'RIGHT_ATTACK':  self.__load_image(BILL_GATES_RIGHT_ATTACK)
        }

        self.direction = pygame.math.Vector2()
        self.speed = speed

        self.playable_surface = None

        self.attack_charged = True

        self.hadouken_sound = pygame.mixer.Sound(HADOUKEN_SOUND)
        self.hadouken_sound.set_volume(0.2)

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
            self.image = self.movements['UP' + ('_ATTACK' if keys[pygame.K_m] or keys[pygame.K_l] else '')]
        elif keys[pygame.K_s]:
            self.direction.y = 1
            self.image = self.movements['DOWN' + ('_ATTACK' if keys[pygame.K_m] or keys[pygame.K_l] else '')]
        else:
            self.direction.y = 0
            self.image = self.movements['STATIC' + ('_ATTACK' if keys[pygame.K_m] or keys[pygame.K_l] else '')]

        if keys[pygame.K_q]:
            self.direction.x = -1
            self.image = self.movements['LEFT' + ('_ATTACK' if keys[pygame.K_m] or keys[pygame.K_l] else '')]
        elif keys[pygame.K_d]:
            self.direction.x = 1
            self.image = self.movements['RIGHT' + ('_ATTACK' if keys[pygame.K_m] or keys[pygame.K_l] else '')]
        else:
            self.direction.x = 0

        if keys[pygame.K_l] and self.attack_charged:
            self.Hadouken(self, self.groups())
            pygame.mixer.Sound.play(self.hadouken_sound)
            self.attack_charged = False
        elif keys[pygame.K_m] and self.attack_charged:
            self.attack()
            self.attack_charged = False
        elif not (keys[pygame.K_m] or keys[pygame.K_l]):
            self.attack_charged = True

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

    class Hadouken(pygame.sprite.Sprite):
        def __init__(self, player: Player, *groups: pygame.sprite.AbstractGroup) -> None:
            super().__init__(*groups)

            self.owner = player

            owner_direction = self.owner.direction.copy()
            if owner_direction == pygame.math.Vector2(0,0):
                self.direction = pygame.math.Vector2(0,1)
            else:
                self.direction = owner_direction
            self.speed = HADOUKEN_SPEED

            surface = pygame.image.load(HADOUKEN_IMAGE).convert_alpha()
            self.image = pygame.transform.scale(surface, (PLAYER_WIDTH, PLAYER_WIDTH))
            self.rect = self.image.get_rect()
            self.rect.center = self.owner.rect.center

        def update(self):
            if self.alive():
                self.rect.center += self.direction * self.speed

                touched = False
                hits = pygame.sprite.spritecollide(self, self.owner.ennemies, False)
                for ennemy in hits:
                    if not ennemy.alive():
                        continue

                    distance = sqrt((ennemy.rect.centerx - self.rect.centerx)**2 + (ennemy.rect.bottom - self.owner.rect.bottom)**2)
                    if distance <= (PLAYER_WIDTH / 3) * 2:
                        ennemy.get_hit(100)
                        self.owner.score += 100
                        touched = True

                if touched:
                    self.kill()