import os
import pygame
from main import WINDOW_SIZE
import numpy as np


def read_map(level):
    """Reads data from file about borders and positions of ball and pocket.

    :return: array, consisting of list of points forming polygon and positions of ball and pocket.
    """
    inp = open("levels/level_" + str(level) + ".txt", 'r')

    ball_pos, pocket_pos, edge, obstacles = [], [], [], []

    for line in inp:
        if len(line.strip()) == 0 or line[0] == '#':
            continue
        line = line.split()

        if line[0] == "ball":
            ball_pos = [int(line[1]), int(line[2])]
        elif line[0] == "pocket":
            pocket_pos = [int(line[1]), int(line[2])]
        elif line[0] == "edge":
            for i in range(1, len(line), 2):
                edge.append([int(line[i]), int(line[i+1])])
        elif line[0] == "obstacle":
            obstacle = []
            for i in range(1, len(line), 2):
                obstacle.append([int(line[i]), int(line[i + 1])])
            obstacles.append(obstacle)

    inp.close()

    return [ball_pos, pocket_pos, edge, obstacles]


def save_map(field, level):
    """Saves field of the level to folder images/levels"""
    field_rect = np.array([field.get_rect()[2], field.get_rect()[3]])
    button_size = np.array([((WINDOW_SIZE[0] - 30 * 4) // 4), (WINDOW_SIZE[1] - 75 - 20 * 3) // 3])
    coefficients = field_rect/button_size
    if coefficients[0] > coefficients[1]:
        field = pygame.transform.smoothscale(field,
                                             (field_rect / coefficients[0]).astype(int))
    else:
        field = pygame.transform.smoothscale(field,
                                             (field_rect / coefficients[1]).astype(int))
    pygame.image.save_extended(field, os.path.join(os.path.dirname(__file__),
                                                   'images/levels', "level_" + str(level) + ".png"))


def save_level_data(constructor):
    """Saves data about level field to file in folder levels"""
    output = open("levels/level_" + str(constructor.level) + ".txt", 'w')

    ball_data = str(int(constructor.ball.pos[0])) + " " + str(int(constructor.ball.pos[1]))
    pocket_data = str(int(constructor.pocket.pos[0])) + " " + str(int(constructor.pocket.pos[1]))
    output.write("ball " + ball_data + "\n")
    output.write("pocket " + pocket_data + "\n")

    edge_data = ""
    for vertex in constructor.obstacles[0].vertices:
        edge_data += str(int(vertex[0])) + " " + str(int(vertex[1])) + " "
    output.write("edge " + edge_data + "\n")

    for i, obstacle in enumerate(constructor.obstacles[1:]):
        obstacle_data = ""
        for vertex in obstacle.vertices:
            obstacle_data += str(int(vertex[0])) + " " + str(int(vertex[1])) + " "
        output.write("obstacle " + obstacle_data + "\n")


def number_of_levels():
    """

    :return: number of levels available.
    """
    return len(os.listdir(path=os.path.join(os.path.dirname(__file__), 'levels')))
