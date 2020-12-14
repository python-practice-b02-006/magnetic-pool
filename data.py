import os
import pygame
from main import WINDOW_SIZE
import numpy as np
import json
import csv


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

    score = get_levels_scores().get(level, 0)

    font = pygame.font.Font(None, 20)
    text = font.render(f"SCORE: {score}", 1, pygame.Color('#e2a000'))
    field_w, field_h = field.get_size()
    new_field = pygame.Surface((field_w, field_h + text.get_height() + 6), pygame.SRCALPHA)

    new_field.blit(field, (0, 0))
    text_rect = text.get_rect()
    text_rect.centerx = field_w // 2
    text_rect.top = field_h + 3
    new_field.blit(text, text_rect)

    pygame.image.save_extended(new_field, os.path.join(os.path.dirname(__file__),
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
    output.close()


def make_level_button_theme(level):
    data = {
        "button": {
            "colours": {
                "normal_bg": "#ffffff",
                "hovered_bg": "#eeeeee",
                "normal_border": "#AAAAAA",
                "hovered_border": "#B0B0B0"
            },
            "misc": {
                "border_width": "2",
                "shadow_width": "0"
            }
        },
        'level_' + str(level): {
            "images": {
                "normal_image": {
                    "path": "images\\levels\\level_" + str(level) + ".png"
                }
            }
        }
    }
    with open("themes/buttons/level_" + str(level) + ".json", "w") as theme_file:
        json.dump(data, theme_file, indent=4)


def number_of_levels():
    """

    :return: number of levels available.
    """
    return len(os.listdir(path=os.path.join(os.path.dirname(__file__), 'levels'))) - 1

def get_levels_scores():
    with open(os.path.join("levels", "high_scores.txt"), "r",  encoding="utf8") as f:
        data = {int(x): int(y) for line in f.readlines() for x, y in [tuple(line.split())]}
    return data

def write_score(level, score):
    data = get_levels_scores()
    if data[level] < score:
        data[level] = score
        with open(os.path.join("levels", "high_scores.txt"), "w", encoding="utf8") as f:
            f.write("\n".join([f"{k} {v}" for k, v in data.items()]))
