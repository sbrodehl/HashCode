import numpy as np
from tqdm import tqdm
from heapq import *
from time import gmtime, strftime

from pqdict import minpq

from IO import *


def cache_to_endpoint(n_cache, endpoints):
    res = np.zeros(shape=(n_cache, len(endpoints)), dtype=np.bool)

    for ep in endpoints:
        for c in ep.con:
            res[c[0]][ep.id] = True

    return res


def vid_to_endpoint(n_vid, n_end, requests):
    res = np.zeros(shape=(n_vid, n_end), dtype=np.bool)

    for r in requests:
        res[r.vid][r.eid] = True

    return res


def solution(n_vid, n_end, n_req, n_cache, s_cache, s_videos, endpoints, requests):
    # solutions
    cache = np.zeros(n_cache)
    videos_on_cache = [[] for _ in range(n_cache)]
    # compute scores
    scores = np.zeros(shape=(n_vid, n_cache), dtype=np.double)
    in_q = np.zeros(shape=(n_vid, n_cache), dtype=np.double)

    pq = minpq()

    c2e = cache_to_endpoint(n_cache, endpoints)
    v2e = vid_to_endpoint(n_vid, n_end, requests)

    for req in tqdm(requests):
        ep = endpoints[req.eid]
        for c in ep.con:
            d_latency = ep.lat - c[1]
            score = req.n * d_latency * (1.0 / s_videos[req.vid])
            scores[req.vid][c[0]] -= score

    for req in tqdm(requests):
        ep = endpoints[req.eid]
        for c in ep.con:
            if not in_q[req.vid][c[0]]:
                in_q[req.vid][c[0]] = True
                # heappush(pq, (scores[req.vid][c[0]], req.vid, c[0]))
                index = req.vid * n_cache + c[0]
                pq[index] = scores[req.vid][c[0]]

    print((len(pq))/(n_vid * n_cache), "in Queue.")

    # update from here on
    while pq:
        # (s, v, c) = heappop(pq)
        key, s = pq.popitem()
        v, c = key // n_cache, key % n_cache
        if cache[c] + s_videos[v] <= s_cache:
            videos_on_cache[c].append(v)
            cache[c] += s_videos[v]

            print(len(pq))

            # update scores for connected caches / videos
            # for req in requests:
            #     if req.vid == v:
            #         ep = endpoints[req.eid]
            #         for ca in ep.con:
            #             d_latency = ep.lat - ca[1]
            #             score = req.n * d_latency * (1.0 / s_videos[req.vid])
            #             scores[req.vid][ca[0]] = 0  # score

            # update scores for connected caches / videos
            for eid in range(n_end):
                # endpoint connects to cache
                if c2e[c][eid]:
                    # if video is requested by the endpoint
                    if v2e[v][eid]:
                        for cc in endpoints[eid].con:
                            scores[v][cc[0]] = 0

            # update the pq
            for (k, ss) in pq.items():
                vv, cc = k // n_cache, k % n_cache
                new_score = scores[vv][cc]
                if ss != new_score:
                    pq[k] = new_score
                # (_, vvvv, cccc) = heappop(pq)
                # heappush(pq, (scores[vvvv][cccc], vvvv, cccc))

        if len(pq) % 100000 == 0:
            write_solution(strftime("%Y%m%d-%H%M%S", gmtime()), cache, videos_on_cache)

    return cache, videos_on_cache
