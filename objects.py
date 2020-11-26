import pygame
import numpy as np


class Ball(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)

    def update(self):
        pass


class Cue(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)

    def update(self):
        pass


class Pocket(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)

    def update(self):
        pass


class Wall(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
