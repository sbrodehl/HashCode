import sys
import numpy as np
from IO import Cell
from best_solution_in_the_wuuuuuuurld import wireless_access
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
