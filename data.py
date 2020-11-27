def read_map(level):
    """Reads data from file about borders and positions of ball and pocket.

    :return: array, consisting of list of points forming polygon and positions of ball and pocket.
    """
    inp = open("levels/level_" + str(level) + ".txt", 'r')

    ball_pos, pocket_pos, edge, obstacle = [], [], [], []

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
                edge.append([line[i], line[i+1]])
        elif line[0] == "obstacle":
            for i in range(1, len(line), 2):
                obstacle.append([line[i], line[i + 1]])

    inp.close()

    return [ball_pos, pocket_pos, edge, obstacle]
