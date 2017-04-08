from Utilities import *
import numpy as np


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
        matrix = np.zeros((H, W))

        for line in range(H):
            tmp = reader.readline()
            for col in range(W):
                if tmp[col] == '-':
                    matrix[line, col] = -1
                elif tmp[col] == '#':
                    matrix[line, col] = 0
                else:
                    matrix[line, col] = 1

        return {
            'height': H,
            'width': W,
            'radius': R,
            'price_backbone': Pb,
            'price_router': Pr,
            'budget': B,
            'backbone': backbone,
            'graph': matrix
        }


def write_solution(fpath, D):
    # look for cables and routers, find positions and write that stuff
    cables = []
    routers = []

    graph = D['graph']
    for x, row in enumerate(graph):
        for y, val in enumerate(row):
            if val == 2:
                cables.append((x,y))
            elif val == 3:
                routers.append((x,y))

    with open(fpath, 'w') as writer:
        writer.write("%d\n" % len(cables))
        for cable in cables:
            writer.write("%d %d\n" % (cable[0], cable[1]))

        writer.write("%d\n" % len(routers))
        for router in routers:
            writer.write("%d %d\n" % (router[0], router[1]))

        writer.close()

if __name__ == '__main__':
    import sys
    fpath = sys.argv[1]
    D = read_dataset(fpath)
    bb = D['backbone']
    D['graph'][bb[0]+1, bb[1]] = 3
    write_solution(sys.argv[2], D)


