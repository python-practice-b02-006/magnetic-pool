import pygame
import numpy as np


class Ball(pygame.sprite.Sprite):
    """
    Attributes:
        pos numpy(int, int): center coordinates
        color (pygame.Color)
        vel numpy(float, float): x and y components of a velocity
    """

    def __init__(self, group, radius, pos, color=pygame.Color("#f600ff")):
        super().__init__(group)
        self.radius = radius
        self.vel = np.zeros(2, dtype=float)
        self.pos = np.array(pos, dtype=float)

        self.image = pygame.Surface((2 * radius, 2 * radius), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (radius, radius), radius)
        self.rect = self.image.get_rect(center=pos)

    def update(self):
        pass


class Cue(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)

    def update(self):
        pass


class Pocket(pygame.sprite.Sprite):
    """Put ball here to win

    Attributes:
        pos numpy(int, int): center coordinates
    """

    def __init__(self, group, radius, pos):
        super().__init__(group)
        self.radius = radius
        self.pos = pos

        self.image = pygame.Surface((2 * radius, 2 * radius), pygame.SRCALPHA)
        pygame.draw.circle(self.image, pygame.Color("black"), (radius, radius), radius)
        self.rect = self.image.get_rect(center=pos)

    def update(self):
        pass


class Obstacle(pygame.sprite.Sprite):
    """An object to stop ball. Draws a polygon on a
    transparent background with size of main window.
    Than you blit it to main surface.

    Attributes:
        window_size (int, int): current size of main window
        border_color, fill_color (pygame.Color)
        vertices (array of tuples (int, int)): vertices of a polygon
    """

    def __init__(self, group, window_size, vertices,
                 fill_color=pygame.Color("#0060ff"),
                 border_color=pygame.Color("#fa0041")):
        super().__init__(group)
        self.vertices = vertices
        self.fill_color = fill_color
        self.border_color = border_color

        self.image = pygame.Surface(window_size, pygame.SRCALPHA)
        pygame.draw.polygon(self.image, fill_color, vertices, 0)
        pygame.draw.polygon(self.image, border_color, vertices, 1)
        self.rect = self.image.get_rect(topleft=(0, 0))
