import pygame
import numpy as np
import os


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
        self.rect = self.image.get_rect(center=self.pos.astype(int))

    def vel_value(self):
        """Returns absolute value of a velocity"""
        return (self.vel ** 2).sum() ** 0.5

    def update(self, b, friction, dt):
        b = np.array([0, 0, b])
        self.pos += self.vel * dt
        vel_abs = np.linalg.norm(self.vel)
        self.vel += np.resize(np.cross(self.vel, b), 2) * dt
        if np.linalg.norm(self.vel) != 0:
            self.vel = self.vel / np.linalg.norm(self.vel) * vel_abs
            self.vel -= friction * self.vel / np.linalg.norm(self.vel) * dt
        self.rect = self.image.get_rect(center=self.pos.astype(int))

    def flip_vel(self, axis, coef_perp=1, coef_par=1):
        """
        Changes the velocity of the ball as if it collided inelastically with a wall with normal vector "axis".
        """
        axis = np.array(axis)
        axis = axis / np.linalg.norm(axis)
        vel_perp = self.vel.dot(axis) * axis
        vel_par = self.vel - vel_perp
        self.vel = -vel_perp * coef_perp + vel_par * coef_par


class Cue(pygame.sprite.Sprite):
    """Handles how user hits the ball.

    Attributes:
        pos numpy(int, int): position where arrow tail sits.
        max_vel (int): maximum initial velocity.
        value (int[0, 100]): percentage of initial velocity.
                             the ball is going to have after hit.
        direction (float, float): cos, sin of angle between x axis and.
                                  direction of a hit.
    """
    def __init__(self, group, pos, max_vel=3):
        super().__init__(group)
        self.pos = pos
        self.value = 30
        self.direction = np.zeros(2, dtype=float)
        self.max_vel = max_vel

        self.image = load_image("cue_arrow.png", -1)
        self.original_image = self.image.copy()
        self.rect = self.image.get_rect(center=(self.rect_center()))

    def get_vel(self):
        return self.value / 100 * self.max_vel * self.direction

    def rect_center(self):
        return list(np.int_(self.pos +
                    self.direction * self.original_image.get_rect().width / 2))

    def change_value(self, value):
        if value > 0:
            self.value += value
            if self.value > 100:
                self.value = 100
        elif value < 0:
            self.value += value
            if self.value < 0:
                self.value = 0

    def filled_arrow(self):
        im = self.original_image.copy()
        arr = pygame.PixelArray(im)
        w, h = self.original_image.get_rect().size
        for x in range(int(w * self.value / 100)):
            for y in range(h):
                if arr[x, y] == 0:
                    arr[x, y] = pygame.Color("#00ff12")
        return im

    def update(self, mouse_pos):
        mouse_vector = np.array(mouse_pos) - self.pos
        if (mouse_vector ** 2).sum() != 0:
            self.direction = mouse_vector / (mouse_vector ** 2).sum() ** 0.5

            angle = np.arctan2(*self.direction[::-1])

            self.image, self.rect = rotate(self.filled_arrow(),
                                           np.degrees(angle),
                                           self.pos,
                                           pygame.Vector2(self.original_image.get_rect().width / 2, 0))

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

    def check_win(self, ball_pos):
       return ((ball_pos - self.pos) ** 2).sum() <= self.radius ** 2


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
        self.vertices = np.array(vertices)

        if len(self.vertices) >= 2:
            self.tangent = np.array([(self.vertices[i - 1] - self.vertices[i]) /
                                     np.linalg.norm(self.vertices[i - 1] - self.vertices[i])
                                     for i in range(len(self.vertices))])
            self.normal = np.array([[self.tangent[i][1], -self.tangent[i][0]] for i in range(len(self.vertices))])

        self.fill_color = fill_color
        self.border_color = border_color

        self.image = pygame.Surface(window_size, pygame.SRCALPHA)
        if len(self.vertices) >= 3:
            self.polygon_rect = pygame.draw.polygon(self.image, fill_color, vertices, 0)
            pygame.draw.polygon(self.image, border_color, vertices, 1)
        elif len(self.vertices) == 2:
            pygame.draw.line(self.image, border_color, vertices[0], vertices[1], 1)
        self.rect = self.image.get_rect(topleft=(0, 0))

    def collide(self, ball, update_args):
        distance = np.infty
        # point where the collision happens
        point = np.zeros(2, dtype=float)
        for i in range(len(self.vertices)):
            r_1 = self.vertices[i] - ball.pos
            r_2 = self.vertices[i-1] - ball.pos
            if np.dot(r_1, self.tangent[i])*np.dot(r_2, self.tangent[i]) < 0:
                dist = abs(np.dot(r_1, self.normal[i]))
                p = ball.pos + dist * self.normal[i]
                n = self.normal[i]
            else:
                dist = min(np.linalg.norm(r_1), np.linalg.norm(r_2))
                if dist == np.linalg.norm(r_1):
                    p = self.vertices[i]
                    n = self.normal[i]
                else:
                    p = self.vertices[i-1]
                    n = self.normal[i]
            if dist < distance:
                point = p
                distance = dist
                normal = n
        if distance > ball.radius:
            return
        collision_axis = ball.pos - point
        ball.update(*update_args)
        ball.flip_vel(collision_axis)
        return True


class MagneticField():
    """
    manages magnetic field and creates it's image to blit on screen.

    in order to change field value while ball isnt moving put your mouse
    inside red border and scroll the mousewheel.

    if you click left mouse button field value goes to zero

    when ball is running no matter where you scroll
    Attributes:
        value (int): initial value of field
        max_height (int): height of the image
        max_value (int): maximum value of field
        pos (left x, center y): coordinates of the image
    """
    def __init__(self, value, max_value=0.15, max_height=200, pos=(10, 300)):
        self.value = value
        self.max_value = max_value
        self.max_height = max_height
        self.pos = pos

        im = load_image("magnetic_arrow.png", -1)
        self.arrow = pygame.transform.scale(im, (60, 60))
        self.min_value = self.arrow.get_size()[1] / self.max_height * self.max_value
        self.image, self.rect = self.create_image()

    def create_image(self):
        arrow_width = self.arrow.get_size()[0]
        main_image = pygame.Surface((arrow_width + 2, 2 * self.max_height + 2), pygame.SRCALPHA)
        pygame.draw.rect(main_image, pygame.Color("red"), (0, 0, *main_image.get_size()), 1)
        main_rect = main_image.get_rect()
        main_rect.centery = self.pos[1]
        main_rect.left = self.pos[0]
        if abs(self.value) < self.min_value:
            return main_image, main_rect
        image = pygame.Surface((arrow_width, self.get_height()), pygame.SRCALPHA)
        rect = image.get_rect()
        rect.bottom = self.max_height

        pygame.draw.rect(image, pygame.Color("#2d34e1"),
                        (arrow_width // 3, arrow_width // 2,
                         arrow_width // 3, self.get_height()))
        image.blit(self.arrow, self.arrow.get_rect(topleft=(0, 0)))
        if self.value < 0:
            image = pygame.transform.rotate(image, 180)
            rect.top = self.max_height
        main_image.blit(image, rect)
        return main_image, main_rect

    def get_height(self):
        return abs(self.value) / self.max_value * self.max_height

    def get_value(self):
        return self.get_height() / self.max_height * self.max_value

    def change_value(self, sign):
        value = sign * 0.01
        if value > 0:
            if self.value == 0:
                self.value = self.min_value
            else:
                self.value += value
                if self.value > self.max_value:
                    self.value = self.max_value
        elif value < 0:
            if self.value == 0:
                self.value = -self.min_value
            else:
                self.value += value
                if self.value < -self.max_value:
                    self.value = -self.max_value
        if abs(self.value) < self.min_value:
            self.value = 0
        self.image, self.rect = self.create_image()

    def zero_value(self):
        self.value = 0
        self.image, self.rect = self.create_image()


def rotate(surface, angle, pivot, offset):
    """Rotate the surface around the pivot point.
    Args:
        surface (pygame.Surface): surface to be rotated.
        angle (float): degrees.
        pivot (tuple: pivot point coords.
        offset (pygame.math.Vector2): this vector is added to the pivot.
    """
    rotated_image = pygame.transform.rotate(surface, -angle)
    rotated_offset = offset.rotate(angle)
    rect = rotated_image.get_rect(center=pivot + rotated_offset)
    return rotated_image, rect


def load_image(name, colorkey=None):
    fullname = os.path.join(os.path.dirname(__file__), 'images', name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image
