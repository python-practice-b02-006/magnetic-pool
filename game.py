import pygame
import objects
import data
from main import WINDOW_SIZE


class Game:
    def __init__(self, level):
        """Creates a game:
        1) Reads data about this level from file. Creates a map of the level (self.map) and puts it on the surface
        self.field.
        2) Creates a ball at the starting position, creates a target, puts them on self.field.

        :param level: number of level.
        """

        # part of window where game is played. In the rest of the window are buttons
        self.game_size = (WINDOW_SIZE[0], WINDOW_SIZE[1]*0.8)
        self.field = pygame.Surface(self.game_size)
        pygame.draw.rect(self.field, pygame.Color("white"), ((0, 0), (WINDOW_SIZE[0], WINDOW_SIZE[1]*0.8)))

        self.ball = None
        self.pocket = None
        self.obstacles = None
        self.map_data = data.read_map(level)
        self.map = self.make_map(self.map_data, self.field)

        self.B = 0

    def make_map(self, map_data, field):
        return pygame.draw.rect(self.field, pygame.Color("#3cb371"), ((350, 275), (100, 50)))

    def update(self, event):
        """
        Updates positions of the ball and the target.
        """
        pass
