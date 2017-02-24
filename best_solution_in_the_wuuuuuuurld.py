import numpy as np
from tqdm import tqdm
from heapq import *


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
    pq = []

    c2e = cache_to_endpoint(n_cache, endpoints)
    v2e = vid_to_endpoint(n_vid, n_end, requests)

    v2c = np.zeros(shape=(n_vid, n_cache), dtype=np.double)

    # build v2c
    for vid in range(n_vid):
        for cid in range(n_cache):
            v2c[vid][cid] = s_videos[vid]

    diff_lat = np.zeros(shape=(n_end, n_cache), dtype=np.int)

    # build diff_lat matrix
    for ep in endpoints:
        for c in ep.con:
            diff_lat[ep.id][c[0]] = ep.lat - c[1]

    for req in tqdm(requests):
        ep = endpoints[req.eid]
        for c in ep.con:
            d_latency = ep.lat - c[1]
            score = req.n * d_latency * (1.0 / s_videos[req.vid])
            scores[req.vid][c[0]] -= score

    for req in tqdm(requests):
        ep = endpoints[req.eid]
        for c in ep.con:
            heappush(pq, (scores[req.vid][c[0]], req.vid, c[0]))

    print((len(pq))/(n_vid * n_cache), "in Queue.")

    # update from here on
    while pq:
        (s, v, c) = heappop(pq)

        if cache[c] + s_videos[v] <= s_cache:
            videos_on_cache[c].append(v)
            cache[c] += s_videos[v]

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
            for i in range(len(pq)):
                (_, vvvv, cccc) = heappop(pq)
                heappush(pq, (scores[vvvv][cccc], vvvv, cccc))

        print(len(pq))

    return cache, videos_on_cache
