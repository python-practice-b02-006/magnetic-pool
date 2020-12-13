import pygame
import objects
import data
import numpy as np
from main import WINDOW_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT,  BG_COLOR
import matplotlib.pyplot as plt


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
        self.B = objects.MagneticField(0.05)
        self.friction = 0.01

        self.score = 10
        self.first_hit = True

        self.map_data = data.read_map(level)
        self.make_map(level)

    def make_map(self, level):
        self.ball = objects.Ball(self.all_sprites, 10, self.map_data[0])
        self.cue = objects.Cue(self.all_sprites, self.ball.pos, max_vel=15)
        self.pocket = objects.Pocket(self.all_sprites, 10, self.map_data[1])
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
            self.field.blit(self.B.image, self.B.rect)
            self.display_score()
        self.field.blit(self.pocket.image,
                        (self.pocket.pos[0] - self.pocket.radius,
                         self.pocket.pos[1] - self.pocket.radius))
        if self.ball.vel_value() < 0.01 and not self.win:
            self.field.blit(self.cue.image, self.cue.rect)
            self.ball.vel = np.zeros(2, dtype=float)

        if self.win:
            self.field.blit(win_screen(self.score), (0, 0))

    def display_score(self):
        font = pygame.font.Font(None, 30)
        text = font.render(f"SCORE: {self.score}", 1, pygame.Color('black'))
        text_x = 20
        text_y = 20
        text_w = text.get_width()
        text_h = text.get_height()
        self.field.blit(text, (text_x, text_y))
        pygame.draw.rect(self.field, (0, 255, 0), (text_x - 10, text_y - 10,
                                               text_w + 20, text_h + 20), 1)

    def reduce_score(self, value):
        self.score -= value
        if self.score < 0:
            self.score = 0

    def update(self, events, dt):
        """
        Updates positions of the ball and the target.
        """
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                btn = event.button
                if btn == 3: # leftclick
                    self.B.zero_value()
                if self.ball.vel_value() == 0:
                    if btn == 1:  # rightclick
                        if self.first_hit:
                            self.first_hit = False
                        else:
                            self.reduce_score(2)

                        self.ball.vel = self.cue.get_vel()
                    if self.B.rect.collidepoint(event.pos):
                        if btn == 4:  # mousewheel up
                            self.B.change_value(1)
                        if btn == 5:  # mousewheel down
                            self.B.change_value(-1)
                    else:
                        if self.ball.vel_value() == 0:
                            if btn == 4:  # mousewheel up
                                self.cue.change_value(5)
                            if btn == 5:  # mousewheel down
                                self.cue.change_value(-5)
                else:
                    if btn == 4:  # mousewheel up
                        self.B.change_value(1)
                    if btn == 5:  # mousewheel down
                        self.B.change_value(-1)

        self.cue.update(pygame.mouse.get_pos())
        self.cue.pos = self.ball.pos

        collided = False
        for obstacle in self.obstacles:
            if obstacle.collide(self.ball)[0]:
                collided = True

        if collided:
            self.reduce_score(1)

        self.ball.update(self.B.value, self.friction, dt)

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
        self.stages = {0: "obstacles", 1: "pocket", 2: "ball", 3: "done"}
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
                    if self.stage == 0 and len(self.obstacles) > self.obstacle_number:
                        if len(self.obstacles[self.obstacle_number].vertices) > 2:  # if obstacle is at least a line
                            self.obstacle_number += 1
                            self.line_pos = []
                        else:
                            self.obstacles.pop()

        if self.stage == 3:
            data.save_level_data(self)
            data.save_map(self.field.subsurface(self.obstacles[0].polygon_rect), self.level)
            data.make_level_button_theme(self.level)

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
        self.display_stage()

    def display_stage(self):
        font = pygame.font.Font(None, 30)
        text = font.render(f"Stage: {self.stages[self.stage]}", 1, pygame.Color('black'))
        text_x = 20
        text_y = 20
        text_w = text.get_width()
        text_h = text.get_height()
        self.field.blit(text, (text_x, text_y))
        pygame.draw.rect(self.field, (0, 255, 0), (text_x - 10, text_y - 10,
                                               text_w + 20, text_h + 20), 1)


class ChaosStudy:
    def __init__(self, level):
        self.field = pygame.Surface(WINDOW_SIZE)
        pygame.draw.rect(self.field, pygame.Color("white"), ((0, 0), WINDOW_SIZE))

        self.stop = False

        self.all_sprites = pygame.sprite.Group()

        self.ball_number = 15  # number of balls being simulated is

        self.balls = []
        self.cue = None
        self.obstacles = None
        self.B = objects.MagneticField(0.05)
        self.friction = 0.0

        self.map_data = data.read_map(level)
        self.make_map()

        self.d_angle = np.pi / 200
        self.d_coord = 2

        self.plot_on = False
        self.length = []
        self.angles = []
        for i in range(self.ball_number):
            self.length.append([])
            self.angles.append([])

    def make_map(self):
        # edges of the field
        self.obstacles = [objects.Obstacle(self.all_sprites, WINDOW_SIZE, self.map_data[2])]
        # obstacles on the field
        for i, obstacle in enumerate(self.map_data[3]):
            self.obstacles.append(objects.Obstacle(self.all_sprites, WINDOW_SIZE, self.map_data[3][i],
                                                   fill_color=pygame.Color("white")))

        self.draw_on_field()

    def draw_on_field(self):
        self.field.fill(BG_COLOR)
        for i in range(len(self.obstacles)):
            self.field.blit(self.obstacles[i].image, (0, 0))
        self.field.blit(self.B.image, self.B.rect)
        for ball in self.balls:
            self.field.blit(ball.image,
                            (ball.pos[0] - ball.radius,
                             ball.pos[1] - ball.radius))
        if len(self.balls) >= 1 and self.balls[0].vel_value() == 0:
            self.field.blit(self.cue.image, self.cue.rect)

    def update(self, events, dt):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                btn = event.button
                if len(self.balls) == 0:
                    if btn == 1:
                        self.make_balls(event)
                        self.cue = objects.Cue(self.all_sprites, self.balls[0].pos, max_vel=15)
                    if self.B.rect.collidepoint(event.pos):
                        if btn == 4:  # mousewheel up
                            self.B.change_value(1)
                        if btn == 5:  # mousewheel down
                            self.B.change_value(-1)
                elif self.balls[0].vel_value() == 0:
                    if btn == 1:  # rightclick
                        self.set_vel(self.cue.get_vel())
                    if self.B.rect.collidepoint(event.pos):
                        if btn == 4:  # mousewheel up
                            self.B.change_value(1)
                        if btn == 5:  # mousewheel down
                            self.B.change_value(-1)
                    else:
                        if self.balls[0].vel_value() == 0:
                            if btn == 4:  # mousewheel up
                                self.cue.change_value(5)
                            if btn == 5:  # mousewheel down
                                self.cue.change_value(-5)
            elif event.type == pygame.KEYDOWN:
                if self.balls[0].vel_value() == 0 and event.key == pygame.K_LEFT:
                    self.balls = []
                    self.cue = None
                elif event.key == pygame.K_SPACE:
                    if self.stop:
                        self.plot_on = False
                    self.stop = not self.stop

        if self.cue is not None:
            self.cue.update(pygame.mouse.get_pos())
            self.cue.pos = self.balls[0].pos

        # cycles that check for collisions and put points on Poincare section
        if not self.stop:
            for i, ball in enumerate(self.balls):
                if np.linalg.norm(ball.vel) > 0:
                    for obstacle in self.obstacles:
                        data = obstacle.collide(ball)
                        if obstacle == self.obstacles[0] and data[0]:
                            # put a point on the section
                            length = self.boundary_coords(data[1], data[2])
                            angle = np.dot(ball.vel/np.linalg.norm(ball.vel), obstacle.tangent[data[2]])
                            self.length[i].append(length)
                            self.angles[i].append(angle)

            for ball in self.balls:
                ball.update(self.B.value, self.friction, dt)
        elif not self.plot_on:
            self.draw_section()

    def make_balls(self, event):
        ball_coords = [np.array(event.pos)]
        self.balls.append(objects.Ball(self.all_sprites, 10, ball_coords[0]))
        for i in range(self.ball_number * 10):
            if len(self.balls) < self.ball_number:
                color = pygame.Color(np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255))
                coords = ball_coords[0] + self.d_coord * (np.random.rand(2) - 0.5 * np.ones(2))
                new_ball = objects.Ball(self.all_sprites, 10, coords, color=color)
                collide = False
                for obstacle in self.obstacles:
                    if obstacle.collide(new_ball)[0]:
                        collide = True
                        break
                if not collide:
                    self.balls.append(new_ball)
            else:
                break

    def set_vel(self, vel):
        vel = np.array(vel)
        for ball in self.balls:
            if ball == self.balls[0]:
                ball.vel = vel
            else:
                angle = self.d_angle * (np.random.rand() - 0.5)
                new_vel = np.dot(np.array([[np.cos(angle), np.sin(angle)], [-np.sin(angle), np.cos(angle)]]), vel)
                ball.vel = new_vel

    def boundary_coords(self, point, vertex_num):
        if vertex_num == 0:
            vertex_num = len(self.obstacles[0].vertices - 1)
        coord = 0
        for i in range(vertex_num-1):
            coord += np.linalg.norm(self.obstacles[0].vertices[i+1] - self.obstacles[0].vertices[i])
        coord += np.linalg.norm(point - self.obstacles[0].vertices[vertex_num-1])
        return coord

    def draw_section(self):
        self.plot_on = True
        plot = plt.figure()
        section = plot.add_subplot(111)
        section.set_ylim(-1.05, 1.05)
        section.set_xlim(0, self.boundary_coords(self.obstacles[0].vertices[0], len(self.obstacles[0].vertices)))
        section.set_xlabel("$\\xi $")
        section.set_ylabel("$\\cos \\varphi$")
        for i, vertex in enumerate(self.obstacles[0].vertices):
            length = self.boundary_coords(vertex, i) * np.ones(2)
            angle = np.array([-1.05, 1.05])
            section.plot(length, angle, color="blue")
        for i, ball in enumerate(self.balls):
            color = (ball.color[0]/255, ball.color[1]/255, ball.color[2]/255)
            section.scatter(self.length[i], self.angles[i], color=color, s=20)
        plt.show()
