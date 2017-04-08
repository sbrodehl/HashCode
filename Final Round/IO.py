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


def write_solution(filepath, d):
    pass

if __name__ == '__main__':
    import sys
    fpath = sys.argv[1]
    print(read_dataset(fpath))
