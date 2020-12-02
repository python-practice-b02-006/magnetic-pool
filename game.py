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
        self.game_size = (WINDOW_SIZE[0], WINDOW_SIZE[1] - 75)
        self.field = pygame.Surface(self.game_size)
        pygame.draw.rect(self.field, pygame.Color("white"), ((0, 0), self.game_size))

        self.all_sprites = pygame.sprite.Group()

        self.ball = None
        self.cue = None
        self.pocket = None
        self.edge = None
        self.map_data = data.read_map(level)
        self.make_map()

        self.B = 0

    def make_map(self):
        self.ball = objects.Ball(self.all_sprites, 10, self.map_data[0])
        # self.cue = objects.Cue(self.all_sprites, self.ball)
        self.pocket = objects.Pocket(self.all_sprites, 10, self.map_data[1])
        self.edge = objects.Obstacle(self.all_sprites, WINDOW_SIZE, self.map_data[2])

        self.field.blit(self.edge.image, (0, 0))
        self.field.blit(self.ball.image,
                        (self.ball.pos[0] - self.ball.radius,
                         self.ball.pos[1] - self.ball.radius))
        self.field.blit(self.pocket.image,
                        (self.pocket.pos[0] - self.ball.radius,
                         self.pocket.pos[1] - self.ball.radius))

    def update(self, event):
        """
        Updates positions of the ball and the target.
        """
        if self.ball.vel_value() == 0 or 1:
            if event.button == 1: # right click
                self.ball.vel = self.cue.get_vel()
            if event.button == 4: # mousewheel up
                self.cue.value += 5
            if event.button == 5: # mousewheel down
                self.cue.value -= 5

            mouse_vector = np.array([event.pos[0] - self.cue.pos[0],
                                    [event.pos[1] - self.cue.pos[1]]], dtype=float)
            self.cue.direction = mouse_vector / (mouse_vector ** 2).sum()
            self.cue.update(event.pos)
            print(1)
