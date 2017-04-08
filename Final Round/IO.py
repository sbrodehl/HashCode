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

        return {'H': H, 'W': W, 'R': R, 'Pb': Pb, 'Pr': Pr, 'B': B,
                'backbone': backbone, 'graph': matrix}


def write_solution(filepath, videos_on_cache):
    used_caches = 0
    for cache in videos_on_cache:
        if len(cache):
            used_caches += 1

    with open(filepath, 'w') as f:
        f.write(str(used_caches))
        f.write('\n')
        for idx, c in enumerate(videos_on_cache):
            if len(c):
                out = str(idx) + " " + " ".join(str(i) for i in c)
                f.write(out)
                f.write('\n')


if __name__ == '__main__':
    import sys
    fpath = sys.argv[1]
    print(read_dataset(fpath))
