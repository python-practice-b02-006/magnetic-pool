import pygame
import numpy as np
import os
from main import DT


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

    def update(self):
        self.pos = self.pos + self.vel * DT
        self.rect.pos = self.pos.astype(int)

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
    """Handles how user hits the ball

    Attributes:
        pos numpy(int, int): position where arrow tail sits
        max_vel (int): maximum initial velocity
        value (int[0, 100]): percentage of initial velocity
                             the ball is going to have after hit
        direction (float, float): cos, sin of angle between x axis and
                                  direction of a hit
    """
    def __init__(self, group, pos, max_vel=5):
        super().__init__(group)
        self.pos = pos
        self.value = 30
        self.direction = np.zeros(2, dtype=float)
        self.max_vel = max_vel

        self.image = load_image("arrow.png", -1)
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
        self.direction = mouse_vector / (mouse_vector ** 2).sum()

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
        self.vertices = np.array(vertices)

        self.tangent = np.array([self.vertices[i-1] - self.vertices[i] for i in range(len(self.vertices))])
        self.tangent = self.tangent / np.linalg.norm(self.tangent)
        # нормаль можно сделать поворотом всех в одну сторону.
        self.normal = np.array([[self.tangent[i][1], -self.tangent[i][0]] for i in range(len(self.vertices))])

        self.fill_color = fill_color
        self.border_color = border_color

        self.image = pygame.Surface(window_size, pygame.SRCALPHA)
        pygame.draw.polygon(self.image, fill_color, vertices, 0)
        pygame.draw.polygon(self.image, border_color, vertices, 1)
        self.rect = self.image.get_rect(topleft=(0, 0))

    def collide(self, ball):
        distance = np.infty
        # point where the collision happens
        point = np.zeros(2, dtype=float)
        for i in range(len(self.vertices)):
            r_1 = self.vertices[i] - ball.pos
            r_2 = self.vertices[i-1] - ball.pos
            if np.dot(r_1, self.tangent[i])*np.dot(r_2, self.tangent[i]) < 0:
                dist = np.dot(r_1, self.normal[i])
                # нормаль может быть неправильного знака
                p = ball.pos + dist * self.normal[i]
            else:
                dist = min(np.linalg.norm(r_1), np.linalg.norm(r_2))
                if dist == np.linalg.norm(r_1):
                    p = self.vertices[i]
                else:
                    p = self.vertices[i-1]
            if dist < distance:
                point = p
                distance = dist
        collision_axis = ball.pos - point
        ball.flip_vel(collision_axis)


def rotate(surface, angle, pivot, offset):
    """Rotate the surface around the pivot point.
    Args:
        surface (pygame.Surface): The surface that is to be rotated.
        angle (float): Rotate by this angle.
        pivot (tuple, list, pygame.math.Vector2): The pivot point.
        offset (pygame.math.Vector2): This vector is added to the pivot.
    """
    rotated_image = pygame.transform.rotate(surface, -angle)  # Rotate the image.
    rotated_offset = offset.rotate(angle)  # Rotate the offset vector.
    # Add the offset vector to the center/pivot point to shift the rect.
    rect = rotated_image.get_rect(center=pivot+rotated_offset)
    return rotated_image, rect  # Return the rotated image and shifted rect.


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