from collections import deque
import numpy as np
import os


class Cell:
    Backbone, Void, Wall, Wireless, Router, ConnectedRouter, Cable = range(-2, 5)


def read_dataset(fpath):
    with open(fpath, 'r') as reader:
        # size of grid
        H, W, R = [int(i) for i in reader.readline().split(" ")]
        # cost and budget
        Pb, Pr, B = [int(i) for i in reader.readline().split(" ")]
        # backbone position
        tmp = reader.readline().split(" ")
        backbone = (int(tmp[0]), int(tmp[1]))
        # read the matrix
        matrix = np.zeros((H, W), dtype=np.int8)

        for line in range(H):
            tmp = reader.readline()
            for col in range(W):
                if tmp[col] == '-':
                    matrix[line, col] = Cell.Void
                elif tmp[col] == '#':
                    matrix[line, col] = Cell.Wall
                else:
                    matrix[line, col] = Cell.Wireless

        return {
            'name': os.path.basename(fpath),
            'height': H,
            'width': W,
            'radius': R,
            'price_backbone': Pb,
            'price_router': Pr,
            'budget': B,
            'original_budget': B,
            'backbone': backbone,
            'graph': matrix,
            'original': matrix.copy()
        }


def _find_solution_paths(d):
    dx = [-1, 0, 1]
    dy = [-1, 0, 1]

    visited = np.zeros((d['height'], d['width']), dtype=np.bool)
    start = d['backbone']

    queue = deque()
    queue.append(start)
    visited[start[0]][start[1]] = True

    cables = []
    routers = []

    while queue:
        cur = queue.popleft()

        if d['graph'][cur] >= Cell.ConnectedRouter:
            cables.append(cur)
        if d['graph'][cur] == Cell.ConnectedRouter:
            routers.append(cur)

        # check neighbors
        for ddx in dx:
            for ddy in dy:
                if ddx == 0 and ddy == 0:
                    continue

                child_x, child_y = cur[0] + ddx, cur[1] + ddy
                # only if still in the grid
                if 0 <= child_x < d['height'] and 0 <= child_y < d['width']:
                    child = (child_x, child_y)
                    # everything is "walkable" cells
                    if not visited[child[0]][child[1]] and d['graph'][child] >= Cell.ConnectedRouter:
                        queue.append(child)
                        visited[child[0]][child[1]] = True

    return cables, routers


def write_solution(fpath, D):
    # look for cables and routers, find positions and write that stuff
    cables, routers = _find_solution_paths(D)

    with open(fpath, 'w') as writer:
        writer.write("%d\n" % len(cables))
        for cable in cables:
            writer.write("%d %d\n" % (cable[0], cable[1]))

        writer.write("%d\n" % len(routers))
        for router in routers:
            writer.write("%d %d\n" % (router[0], router[1]))


if __name__ == '__main__':
    import sys

    fpath = sys.argv[1]
    D = read_dataset(fpath)
    bb = D['backbone']
    D['graph'][bb[0] - 1, bb[1]] = Cell.Cable
    write_solution(sys.argv[2], D)
