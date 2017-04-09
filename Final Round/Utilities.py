import sys
import numpy as np

from IO import Cell
from best_solution_in_the_wuuuuuuurld import wireless_access


def csv_print(mat, fmt='%.5f'):
    np.savetxt(sys.stdout.buffer, mat, fmt=fmt, newline="\n")


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
