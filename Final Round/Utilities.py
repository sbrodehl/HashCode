import sys

import numpy
import numpy as np
from IO import Cell
from tqdm import tqdm
import matplotlib.pyplot as plt


def csv_print(mat, fmt='%.5f'):
    np.savetxt(sys.stdout.buffer, mat, fmt=fmt, newline="\n")


def sort_array_with_id(arr):
    """
    Sort array ascending and keep track of ids.
    :param arr: array with values
    :return: array with tuples (id, val)
    """
    tuple_arr = [(id, arr[id]) for id in range(len(arr))]
    return sorted(tuple_arr, key=lambda t: t[1])


def plot_graph_with_skeleton(d, skel):
    fig = plt.figure()

    plt.imshow(d['graph'])
    plt.axis('off')
    # plt.set_title('original', fontsize=20)

    plt.imshow(skel, cmap=plt.cm.gray, alpha=0.25)
    plt.show()


def compute_solution_score(d):
    # look for cables and routers, compute coverage and cost
    cables = []
    routers = []

    g = d['graph']
    for x, row in enumerate(g):
        for y, val in enumerate(row):
            if val == Cell.Cable:
                cables.append((x, y))
            elif val == Cell.ConnectedRouter:
                routers.append((x, y))
                cables.append((x, y))

    # budget part of scoring
    score_cost = d['budget'] - (len(cables) * d['price_backbone'] + len(routers) * d['price_router'])
    coverage = (d['original'] == Cell.Wireless).astype(np.int8)
    for (a, b) in routers:
        mask = wireless_access(a, b, d)
        for x, row in enumerate(mask):
            for y, val in enumerate(row):
                if mask[x][y]:
                    w = x + a - d['radius']
                    v = y + b - d['radius']
                    coverage[w][v] = 2
    coverage = (coverage == 2).astype(np.int8)
    score = 1000 * np.sum(coverage)
    return np.floor(score + score_cost)


def wireless_access(a, b, d):
    g = d["graph"]
    r = d["radius"]
    mask = np.ones((2 * r + 1, 2 * r + 1))
    for dw in range(-r, r + 1):
        for dh in range(-r, r + 1):
            # skip router cell
            if dh == 0 and dw == 0:
                continue
            # transform coordinates
            x = a + dh
            y = b + dw
            # checking bounds
            if x not in range(0, d["height"]):
                continue
            if y not in range(0, d["width"]):
                continue
            # if this is a wireless cell
            if not g[x][y] == Cell.Wireless:
                # set others fields to zero
                mask[dh + r][dw + r] = 0
                continue
            # construct smallest enclosing rectangle
            rows = range(np.min([a, x]), np.max([a, x]) + 1)
            cols = range(np.min([b, y]), np.max([b, y]) + 1)
            rect = g[rows][:, cols]
            walls = (rect == Cell.Wall).astype(int)
            if np.sum(walls):
                mask[dh + r][dw + r] = 0
            #
            # loop over rectangle and check condition
            # TODO if there is at least one wall cell in closing rectangle condition is true?
            # in_sight = True
            # for w in rows:
            #     for v in cols:
            #         # if this is a wall cell
            #         if not g[w][v] == Cell.Wall:
            #             continue
            #         # check if wall is in 'sight'
            #         if np.min([a, x]) <= w <= np.max([a, x]) and np.min([b, y]) <= v <= np.max([b, y]):
            #             # ALARM!
            #             # TODO some early stopping?
            #             mask[dh + r][dw + r] = 0
            #             in_sight = False
            #             break
            #
            #     if not in_sight:
            #         break
    return mask
