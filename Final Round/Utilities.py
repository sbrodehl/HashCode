import numpy as np
from tqdm import tqdm
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

from IO import Cell, read_dataset


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

    # calculate score
    score_budget = d['budget'] - (len(cables) * d['price_backbone'] + len(routers) * d['price_router'])
    coverage = np.zeros(d['graph'].shape).astype(np.int8)
    for (a, b) in tqdm(routers, desc="Calculating score"):
        mask = wireless_access(a, b, d)
        R = d['radius']
        coverage[(a - R):(a + R + 1), (b - R):(b + R + 1)] |= mask.astype(np.bool)

    score_coverage = 1000 * np.sum(coverage)
    return np.floor(score_coverage + score_budget)


def wireless_access(a, b, d):
    g = d["original"]
    r = d["radius"]
    mask = np.zeros((2 * r + 1, 2 * r + 1))
    for dw in range(-r, r + 1):
        for dh in range(-r, r + 1):
            # skip router cell
            if dh == 0 and dw == 0:
                mask[dh + r][dw + r] = 1
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
            else:
                mask[dh + r][dw + r] = 1
    return mask


def plot_with_coverage(d, fpath=None, show=False):
    # plot graph with coverage
    fig = plt.figure()

    ax = plt.Axes(fig, (0, 0, 1, 1))
    ax.set_axis_off()
    fig.add_axes(ax)
    h = d['height']
    w = d['width']
    dpi = 100
    fig.set_size_inches(10 * w / dpi, 10 * h / dpi)
    ax.imshow(d['graph'], cmap=plt.cm.viridis, extent=(0, 1, 0, 1), aspect='auto', interpolation='none')

    routers = []
    g = d['graph']
    for x, row in enumerate(g):
        for y, val in enumerate(row):
            if val == Cell.ConnectedRouter:
                routers.append((x, y))

    coverage = np.zeros((d['height'], d['width']), dtype=np.bool)
    R = d['radius']
    for r in range(len(routers)):
        a, b = routers[r]
        mask = wireless_access(a, b, d)
        coverage[(a - R):(a + R + 1), (b - R):(b + R + 1)] |= mask.astype(np.bool)

    ax.imshow(coverage, cmap=plt.cm.gray, alpha=0.2, extent=(0, 1, 0, 1), aspect='auto', interpolation='none')

    if fpath is not None:
        plt.savefig(fpath, dpi=dpi)

    if show:
        plt.show()


if __name__ == '__main__':
    import sys

    f_in = sys.argv[1]
    f_out = sys.argv[2]
    d = read_dataset(f_in)

    with open(f_out, 'r') as f:
        n = int(f.readline())
        for i in range(n):
            a, b = [int(i) for i in f.readline().split(" ")]
            d['graph'][a, b] = Cell.Cable
        m = int(f.readline())
        for i in range(m):
            a, b = [int(i) for i in f.readline().split(" ")]
            d['graph'][a, b] = Cell.ConnectedRouter

    print("score %d " % compute_solution_score(d))
    pngfile = f_out
    pngfile = pngfile.replace(".out", ".png")
    plot_with_coverage(d, pngfile, False)
