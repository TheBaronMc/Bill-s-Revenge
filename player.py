import pygame
import time

from math import sqrt
from typing import Dict, Iterable, Tuple, Any, List, Union

from settings import *

class Character(pygame.sprite.Sprite):
    def __init__(self, life: float, image: str, size: Tuple[int, int], *groups: pygame.sprite.AbstractGroup) -> None:
        super().__init__(*groups)

        surface = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(surface, size)
        self.rect = self.image.get_rect()

        self.health = life
            
    def get_damage(self, damage: float):
        self.health -= damage
        if self.health <= 0:
            self.kill()

    def is_dead(self) -> bool:
        return self.active()


class PlayableSurface(pygame.sprite.Sprite):
    def __init__(self, size: Tuple[int, int], *groups: pygame.sprite.AbstractGroup) -> None:
        super().__init__(*groups)

        self.image = pygame.Surface(size)
        #self.image.fill((0,0,255))
        self.rect = self.image.get_rect(topleft=(0, SCREEN_HEIGHT - size[1]))


class MoveableCharacter(Character):
    def __init__(self, speed: int, power: float, life: float, image: str, size: Tuple[int, int], *groups: pygame.sprite.AbstractGroup) -> None:
        super().__init__(life, image, size, *groups)

        self.direction = pygame.math.Vector2()
        self.speed = speed

        self.power: float = power
        self.ennemies: Iterable[Character] = []
        self.score: int = 0

        self.playable_surface: PlayableSurface = None

        self.attack_charged = True

    def add_ennemies(self, *ennemies: Iterable[Character]):
        self.ennemies += ennemies

    def add_ennemy(self, ennemy: Character):
        self.ennemies.append(ennemy)

    def get_ennemies(self) -> Iterable[Character]:
        return self.ennemies

    def set_playable_surface(self, surface: PlayableSurface):
        self.playable_surface = surface

    def attack_special(self):
        pass

    def attack(self):
        hits = pygame.sprite.spritecollide(self, self.ennemies, False)
        for ennemy in hits:
            distance = sqrt((ennemy.rect.centerx - self.rect.centerx)**2 + (ennemy.rect.bottom - self.rect.bottom)**2)
            if distance <= (PLAYER_WIDTH / 3) * 2:
                ennemy.get_damage(self.power)
                self.score += 50
    
    def get_score(self) -> int:
        return self.score

    def move(self):
        pass

    def update(self):
        self.move()
        self.rect.center += self.direction * self.speed
        self.__playable_surface_collisions()

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


class Ennemy(MoveableCharacter):
    def __init__(self, aggressive: bool, speed: int, power: float, life: float, image: str, size: Tuple[int, int], *groups: pygame.sprite.AbstractGroup) -> None:
        super().__init__(speed, power, life, image, size, *groups)

        self.attack_charged = False
        self.last_attack = None
        self.attacking = False

        self.aggressive = aggressive

    def move(self):
        super().move()

        if not self.aggressive:
            return

        # Get the nearest player
        def get_nearest(players: Iterable[Character], nearest_player: Character) -> Character:
                if players == []:
                    return nearest_player
                if nearest_player == None:
                    return get_nearest(players[1:], players[0])
                else:
                    current_player: Character = players[0]
                    shortest_distance = abs(self.rect.centerx - nearest_player.rect.centerx)
                    if abs(current_player.rect.centerx - nearest_player.rect.centerx) < shortest_distance:
                        return get_nearest(players[1:], current_player)
                    else:
                        return get_nearest(players[:1], nearest_player)

        alive_ennemies = list(filter(lambda en: en.alive(), self.ennemies))
            
        nearest_player: Character = get_nearest(alive_ennemies, None)

        if nearest_player == None:
            self.direction.xy = (0,0)
            self.__discharge_attack()
            return

        # Am I close enough?
        if sqrt((nearest_player.rect.centerx - self.rect.centerx)**2 + (nearest_player.rect.bottom - self.rect.bottom)**2) < (PLAYER_WIDTH/3)*2:
            self.__charge_attack()
            if self.attack_charged:
                self.attack()
                self.attacking = True
                self.attack_charged = False
                self.last_attack = time.time()
            self.direction.xy = (0,0)
        else:
            self.__discharge_attack()
            # Move to the nearest player
            if abs(self.rect.centerx - nearest_player.rect.centerx) < (SCREEN_WIDTH/2):
                if nearest_player.rect.centerx < self.rect.centerx:
                    self.direction.x = -1
                elif nearest_player.rect.centerx > self.rect.centerx:
                    self.direction.x = 1
                else:
                    self.direction.x = 0

                if nearest_player.rect.bottom < self.rect.bottom:
                    self.direction.y = -1
                elif nearest_player.rect.bottom > self.rect.bottom:
                    self.direction.y = 1
                else:
                    self.direction.y = 0
            else:
                self.direction.xy = (0,0)

    def attack(self):
        super().attack()
        self.last_attack = time.time()

    def __charge_attack(self):
        if self.last_attack:
            if time.time() - self.last_attack >= 4:
                self.attack_charged = True
            if time.time() - self.last_attack >= 2:
                self.attacking = False
        else:
            self.last_attack = time.time()
    
    def __discharge_attack(self):
        self.last_attack = None
        self.attacking = False
        

class SteveJobs(Ennemy):
    def __init__(self, aggressive: bool, starting_position: Tuple[int,int], *groups: pygame.sprite.AbstractGroup) -> None:
        super().__init__(aggressive, STEVE_JOBS_SPEED, STEVE_JOBS_POWER, STEVE_JOBS_HEALTH, STEVE_JOBS, (PLAYER_WIDTH, PLAYER_HEIGHT), *groups)

        self.images: Dict[str,pygame.Surface] = {
            'NORMAL': self.image,
            'NORMAL_ATTACKED': self.__load_image(STEVE_JOBS_ATTACKED),
            'ATTACK': self.__load_image(STEVE_JOBS_ATTACK),
            'ATTACK_ATTACKED': self.__load_image(STEVE_JOBS_ATTACK_ATTACKED)
        }

        self.rect.bottomleft = starting_position
        self.cry = pygame.mixer.Sound(WILHELM)
        self.cry.set_volume(WILHELM_VOLUME)
        self.sound_played = False
        
        self.attacked = False
        self.attack_animation_duration = 0

    def get_damage(self, damage):
        super().get_damage(damage)
        if not self.sound_played:
            pygame.mixer.Sound.play(self.cry)
            self.sound_played = True
            self.attacked = True
            self.attack_animation_duration = time.time()
            self.image = self.images[('ATTACK' if self.attacking else 'NORMAL') + ('_ATTACKED' if self.attacked else '')]
            
    def update(self, *args: Any, **kwargs: Any) -> None:
        super().update(*args, **kwargs)
        self.image = self.images[('ATTACK' if self.attacking else 'NORMAL') + ('_ATTACKED' if self.attacked else '')]

        if self.attacked and (time.time() - self.attack_animation_duration > 0.5):
            self.attacked = False

    def __load_image(self, image: str) -> pygame.surface.Surface:
        surface = pygame.image.load(image).convert_alpha()
        return pygame.transform.scale(surface, (PLAYER_WIDTH, PLAYER_HEIGHT))



class PlayableCharacter(MoveableCharacter):
    def __init__(self, speed: int, power: float, life: float, image: str, size: Tuple[int, int], *groups: pygame.sprite.AbstractGroup) -> None:
        super().__init__(speed, power, life, image, size, *groups)

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_z]:
            self.direction.y = -1
        elif keys[pygame.K_s]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        if keys[pygame.K_q]:
            self.direction.x = -1
        elif keys[pygame.K_d]:
            self.direction.x = 1
        else:
            self.direction.x = 0

        if keys[pygame.K_l] and self.attack_charged:
            self.attack_special()
            self.attack_charged = False
        elif keys[pygame.K_m] and self.attack_charged:
            self.attack()
            self.attack_charged = False
        elif not (keys[pygame.K_m] or keys[pygame.K_l]):
            self.attack_charged = True



class BillGates(PlayableCharacter):
    def __init__(self, *groups: pygame.sprite.AbstractGroup) -> None:
        super().__init__(BILL_GATES_SPEED, BILL_GATES_NORMAL_ATTACK, BILL_GATES_HEALTH, BILL_GATES_FRONT, (PLAYER_WIDTH, PLAYER_HEIGHT), *groups)

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

        self.hadouken_sound = pygame.mixer.Sound(HADOUKEN_SOUND)
        self.hadouken_sound.set_volume(0.2)

    def attack_special(self):
        super().attack_special()
        pygame.mixer.Sound.play(self.hadouken_sound)
        self.Hadouken(self, self.groups())
    
    def update(self):
        super().update()

        if self.direction.y < 0:
            self.image = self.movements['UP' + ('_ATTACK' if not self.attack_charged else '')]
        elif self.direction.y > 0:
            self.image = self.movements['DOWN' + ('_ATTACK' if not self.attack_charged else '')]
        else:
            self.image = self.movements['STATIC' + ('_ATTACK' if not self.attack_charged else '')]

        if self.direction.x < 0:
            self.image = self.movements['LEFT' + ('_ATTACK' if not self.attack_charged else '')]
        elif self.direction.x > 0:
            self.image = self.movements['RIGHT' + ('_ATTACK' if not self.attack_charged else '')]
        else:
            self.direction.x = 0

    def __load_image(self, image: str) -> pygame.surface.Surface:
        surface = pygame.image.load(image).convert_alpha()
        return pygame.transform.scale(surface, (PLAYER_WIDTH, PLAYER_HEIGHT))

    class Hadouken(pygame.sprite.Sprite):
        def __init__(self, player: PlayableCharacter, *groups: pygame.sprite.AbstractGroup) -> None:
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
                        ennemy.get_damage(BILL_GATES_SPECIAL_ATTACK)
                        self.owner.score += 100
                        touched = True

                if touched:
                    self.kill()