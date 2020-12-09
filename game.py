import pygame
import objects
import data
import numpy as np
from main import WINDOW_SIZE, BG_COLOR
import os


class Game:
    def __init__(self, level):
        """Creates a game:
        1) Reads data about this level from file. Creates a map of the level and puts it on the surface
        self.field.
        2) Creates a ball at the starting position, creates a target, puts them on self.field.

        :param level: number of level.
        """

        self.field = pygame.Surface(WINDOW_SIZE)
        pygame.draw.rect(self.field, pygame.Color("white"), ((0, 0), WINDOW_SIZE))

        self.all_sprites = pygame.sprite.Group()

        self.win = False

        self.ball = None
        self.cue = None
        self.pocket = None
        self.obstacles = None
        self.map_data = data.read_map(level)
        self.make_map(level)
        self.score = 11

        self.B = 0.05
        self.friction = 0.01

    def make_map(self, level):
        self.ball = objects.Ball(self.all_sprites, 10, self.map_data[0])
        self.cue = objects.Cue(self.all_sprites, self.ball.pos, max_vel=15)
        self.pocket = objects.Pocket(self.all_sprites, 20, self.map_data[1])
        # edges of the field
        self.obstacles = [objects.Obstacle(self.all_sprites, WINDOW_SIZE, self.map_data[2])]
        # obstacles on the field
        for i, obstacle in enumerate(self.map_data[3]):
            self.obstacles.append(objects.Obstacle(self.all_sprites, WINDOW_SIZE, self.map_data[3][i],
                                                   fill_color=pygame.Color("white")))

        self.draw_on_field()
        data.save_map(self.field.subsurface(self.obstacles[0].polygon_rect), level)

    def draw_on_field(self):
        self.field.fill(BG_COLOR)
        for i in range(len(self.obstacles)):
            self.field.blit(self.obstacles[i].image, (0, 0))
        if not self.win:
            self.field.blit(self.ball.image,
                            (self.ball.pos[0] - self.ball.radius,
                             self.ball.pos[1] - self.ball.radius))
        self.field.blit(self.pocket.image,
                        (self.pocket.pos[0] - self.pocket.radius,
                         self.pocket.pos[1] - self.pocket.radius))
        if self.ball.vel_value() < 0.01 and not self.win:
            self.field.blit(self.cue.image, self.cue.rect)
            self.ball.vel = np.zeros(2, dtype=float)

        if self.win:
            self.field.blit(win_screen(self.score), (0, 0))

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
                    self.score -= 1
                if btn == 4:  # mousewheel up
                    self.cue.change_value(5)
                if btn == 5:  # mousewheel down
                    self.cue.change_value(-5)

        self.cue.update(pygame.mouse.get_pos())
        self.cue.pos = self.ball.pos

        for obstacle in self.obstacles:
            obstacle.collide(self.ball, [self.B, self.friction, -dt])

        self.ball.update(self.B, self.friction, dt)

        if self.pocket.check_win(self.ball.pos):
            self.ball.vel = np.zeros(2, dtype=float)
            self.win = True


def win_screen(score):
    # зарозовим экран
    fg = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
    fg.fill((224, 99, 201, 128))

    # выведем информацию
    text = ["YOU WIN",  "Score: " + str(score)]
    font = pygame.font.Font(None, 100)
    text_coord = 50
    for line in text:
        string_rendered = font.render(line, 1, pygame.Color('#fff500'))
        line_rect = string_rendered.get_rect()
        text_coord += 10
        line_rect.top = text_coord
        line_rect.x = (WINDOW_SIZE[0] - string_rendered.get_width()) // 2
        text_coord += line_rect.height
        fg.blit(string_rendered, line_rect)

    return fg


class Constructor:
    """Implements interactive creating of levels."""
    def __init__(self, level):
        self.all_sprites = pygame.sprite.Group()

        self.field = pygame.Surface(WINDOW_SIZE)
        self.field.fill(BG_COLOR)
        self.pocket = None
        self.ball = None
        self.obstacles = []
        # stage = 0 - drawing edge and obstacles
        # stage = 1 - picking where pocket is
        # stage = 2 - picking where starting ball position is
        # stage = 3 - end creating level
        self.stage = 0
        self.obstacle_number = 0
        self.line_pos = []

        self.level = level

    def update(self, events):
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                if self.stage == 0:
                    if len(self.obstacles) > self.obstacle_number \
                            and len(self.obstacles[self.obstacle_number].vertices) > 0:
                        start_pos = [self.obstacles[self.obstacle_number].vertices[-1],
                                     self.obstacles[self.obstacle_number].vertices[0]]
                        self.line_pos = [[start_pos[0], event.pos], [start_pos[1], event.pos]]
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.stage == 0:
                        if len(self.obstacles) <= self.obstacle_number:
                            self.obstacles.append(objects.Obstacle(self.all_sprites, WINDOW_SIZE,
                                                                   np.array(event.pos, ndmin=2)))
                        else:
                            if self.obstacle_number:
                                fill_color = pygame.Color("white")
                            else:
                                fill_color = pygame.Color("#0060ff")
                            new_vertices = np.concatenate((self.obstacles[self.obstacle_number].vertices,
                                                           np.array(event.pos, ndmin=2)),
                                                          axis=0)
                            self.obstacles[self.obstacle_number] = objects.Obstacle(self.all_sprites, WINDOW_SIZE,
                                                                                    new_vertices,
                                                                                    fill_color=fill_color)
                    elif self.stage == 1:
                        self.pocket = objects.Pocket(self.all_sprites, 10, event.pos)
                    elif self.stage == 2:
                        self.ball = objects.Ball(self.all_sprites, 10, event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    if self.stage <= 2:
                        self.stage += 1
                elif event.key == pygame.K_LEFT:
                    if self.stage >= 1:
                        self.stage -= 1
                elif event.key == pygame.K_SPACE:
                    self.obstacle_number += 1
                    self.line_pos = []

        if self.stage == 3:
            data.save_level_data(self)
            data.save_map(self.field.subsurface(self.obstacles[0].polygon_rect), self.level)
            self.make_level_button_theme()

    def draw(self):
        self.field.fill(BG_COLOR)
        if len(self.obstacles) >= 0:
            for i in range(len(self.obstacles)):
                self.field.blit(self.obstacles[i].image, (0, 0))
        if self.stage == 0 and len(self.line_pos) > 0:
            pygame.draw.line(self.field, pygame.Color("#fa0041"), self.line_pos[0][0], self.line_pos[0][1], 1)
            pygame.draw.line(self.field, pygame.Color("#fa0041"), self.line_pos[1][0], self.line_pos[1][1], 1)
        if self.pocket is not None:
            self.field.blit(self.pocket.image, self.pocket.rect)
        if self.ball is not None:
            self.field.blit(self.ball.image, self.ball.rect)

    def make_level_button_theme(self):
        pass


