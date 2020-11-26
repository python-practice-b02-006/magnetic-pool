import pygame
import objects
import data


class Game:
    def __init__(self, level):
        """Creates a game:
        1) Reads data about this level from file. Creates a map of the level (self.map) and puts it on the surface
        self.field.
        2) Creates a ball at the starting position, creates a target, puts them on self.field.

        :param level: number of level.
        """
        self.field = pygame.Surface((750, 500))
        self.map = pygame.draw.rect(self.field, pygame.Color("#3cb371"), ((300, 250), (200, 100)))

    def update(self, event):
        """
        Updates positions of the ball and the target.
        """
        pass
