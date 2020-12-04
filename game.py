import pygame
import objects
import data
import numpy as np
from main import WINDOW_SIZE, BG_COLOR


class Game:
    def __init__(self, level):
        """Creates a game:
        1) Reads data about this level from file. Creates a map of the level and puts it on the surface
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
        self.obstacles = None
        self.map_data = data.read_map(level)
        self.make_map()

        self.B = 0.05
        self.friction = 0.005

    def make_map(self):
        self.ball = objects.Ball(self.all_sprites, 10, self.map_data[0])
        self.cue = objects.Cue(self.all_sprites, self.ball.pos, max_vel=5)
        self.pocket = objects.Pocket(self.all_sprites, 10, self.map_data[1])
        # edges of the field
        self.obstacles = [objects.Obstacle(self.all_sprites, WINDOW_SIZE, self.map_data[2])]
        # obstacles on the field
        for obstacle in self.map_data[3]:
            self.obstacles.append(objects.Obstacle(self.all_sprites, WINDOW_SIZE, self.map_data[2],
                                                   fill_color=pygame.Color("white")))

        self.draw_on_field()

    def draw_on_field(self):
        self.field.fill(BG_COLOR)
        for i in range(len(self.obstacles)):
            self.field.blit(self.obstacles[i].image, (0, 0))
        self.field.blit(self.ball.image,
                        (self.ball.pos[0] - self.ball.radius,
                         self.ball.pos[1] - self.ball.radius))
        self.field.blit(self.pocket.image,
                        (self.pocket.pos[0] - self.ball.radius,
                         self.pocket.pos[1] - self.ball.radius))
        if self.ball.vel_value() < 0.01:
            self.field.blit(self.cue.image, self.cue.rect)
            self.ball.vel = np.zeros(2, dtype=float)

    def update(self, events, dt):
        """
        Updates positions of the ball and the target.
        """
        for event in events:
            if self.ball.vel_value() < 0.01 and event.type == pygame.MOUSEBUTTONDOWN:
                self.ball.vel = np.zeros(2, dtype=float)
                btn = event.button
                if btn == 1:  # right click
                    self.ball.vel = self.cue.get_vel()
                if btn == 4:  # mousewheel up
                    self.cue.change_value(5)
                if btn == 5:  # mousewheel down
                    self.cue.change_value(-5)

        self.cue.update(pygame.mouse.get_pos())
        self.cue.pos = self.ball.pos

        for obstacle in self.obstacles:
            obstacle.collide(self.ball, [self.B, self.friction, -dt])

        self.ball.update(self.B, self.friction, dt)
