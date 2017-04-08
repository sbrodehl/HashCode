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


def build_graph(n_vid, n_end, n_req, n_cache, s_cache, s_videos, endpoints, requests):
    graph = {
        'n_videos': n_vid,
        'n_endpoints': n_end,
        'n_requests': n_req,
        'n_caches': n_cache,
        'max_cache_size': s_cache,
        'requests': requests,
        'caches': [{} for _ in range(n_cache)],
        'videos': [{} for _ in range(n_vid)],
        'endpoints': [{} for _ in range(n_end)]
    }

    tqdm.write("Setting up Graph")

    # insert caches with corresponding endpoints
    for c in tqdm(range(n_cache), desc="Caches"):
        graph['caches'][c] = {
            'endpoints': [],
            'size': s_cache
        }

    # insert endpoints with corresponding requests
    for e in tqdm(range(n_end), desc="Caches + Endpoints"):
        graph['endpoints'][e] = {
            'latency': endpoints[e].lat,
            'connections': endpoints[e].con,
            'requests': []
        }
        for con in endpoints[e].con:
            graph['caches'][con[0]]['endpoints'].append(e)

    # insert videos with corresponding requests
    for v in tqdm(range(n_vid), desc="Videos"):
        graph['videos'][v] = {
            'size': s_videos[v],
            'requests': []
        }

    for i, r in tqdm(enumerate(requests), desc="Inserting Requests"):
        graph['videos'][r.vid]['requests'].append(i)
        graph['endpoints'][r.eid]['requests'].append(i)

    return graph


if __name__ == '__main__':
    import sys
    fpath = sys.argv[1]
    print(read_dataset(fpath))