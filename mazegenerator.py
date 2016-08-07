import random
from random import shuffle, randrange, randint


def make_maze(w=12, h=11):
    vis = [[0] * w + [1] for _ in range(h)] + [[1] * (w + 1)]
    ver = [["#  "] * w + ['#'] for _ in range(h)] + [[]]
    hor = [["###"] * w + ['#'] for _ in range(h + 1)]

    def walk(x, y):
        vis[y][x] = 1

        d = [(x - 1, y), (x, y + 1), (x + 1, y), (x, y - 1)]
        shuffle(d)
        for (xx, yy) in d:
            if vis[yy][xx]: continue
            if xx == x: hor[max(y, yy)][x] = "#  "
            if yy == y: ver[y][max(x, xx)] = "   "
            walk(xx, yy)

    walk(randrange(w), randrange(h))

    s = ""
    for (a, b) in zip(hor, ver):
        s += ''.join(a + ['\n'] + b + ['\n'])
    return s


def create_maze():
    tmp = make_maze()
    cur_maze = tmp.split("\n")
    maze = []

    for line in cur_maze:
        maze.append(line)

    maze = maze[0:-2]

    return maze
