from Utilities import *


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


def read_dataset(fpath):
    with open(fpath, 'r') as reader:
        # numbers
        n_vid, n_end, n_req, n_cache, s_cache = [int(i) for i in reader.readline().split(" ")]

        # video sizes
        s_videos = [int(i) for i in reader.readline().split(" ")]

        # endpoints
        endpoints = []
        for e in range(n_end):
            L_D, K = [int(i) for i in reader.readline().split(" ")]

            connections = []

            # iterate over the K connected caches
            for k in range(K):
                c, L_C = [int(i) for i in reader.readline().split(" ")]
                connections.append((c, L_C))

            endpoints.append(Endpoint(e, L_D, connections))

        # requests
        requests = []
        for r in range(n_req):
            R_v, R_e, R_n = [int(i) for i in reader.readline().split(" ")]
            requests.append(Request(R_v, R_e, R_n))

        return n_vid, n_end, n_req, n_cache, s_cache, s_videos, endpoints, requests


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
