import numpy as np
from tqdm import tqdm

from Utilities import Scoring

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

    c2e = cache_to_endpoint(n_cache, endpoints)
    v2e = vid_to_endpoint(n_vid, n_end, requests)

    v2c = np.zeros(shape=(n_vid, n_cache), dtype=np.double)

    # build v2c
    for vid in range(n_vid):
        for cid in range(n_cache):
            v2c[vid][cid] = s_videos[vid]

    # update step
    def update(cid, vid, benefit):
        v2c[vid][cid] /= benefit

        # for k, ep in enumerate(c2e[cid]):
        #     if ep and v2e[vid][k]:
        #         # update diff_lat for end k
        #         diff_lat[k][cid] =

    diff_lat = np.zeros(shape=(n_end, n_cache), dtype=np.int)

    # build diff_lat matrix
    for ep in endpoints:
        for c in ep.con:
            diff_lat[ep.id][c[0]] = ep.lat - c[1]

    cache = np.zeros(n_cache)
    videos_on_cache = [[] for _ in range(n_cache)]

    # update from here on
    done = False
    iter = 0
    while not done:
        # compute scores
        scores = np.zeros(shape=(n_vid, n_cache), dtype=np.double)

        for req in tqdm(requests):
            ep = endpoints[req.eid]
            for c in ep.con:
                if req.vid not in videos_on_cache[c[0]]:
                    d_latency = diff_lat[ep.id][c[0]]
                    score = req.n * d_latency * (1.0 / v2c[req.vid][c[0]])
                    scores[req.vid][c[0]] += score

        tscores = []

        for v in range(n_vid):
            for c in range(n_cache):
                if v in videos_on_cache[c]:
                    break
                tscores.append(Scoring(v, c, scores[v][c]))

        s_scores = sorted(tscores, key=lambda x: x[0])

        found = False
        for t in s_scores:
            c = t.cid
            v = t.vid
            s = t.score
            if cache[c] + s_videos[v] <= s_cache:
                videos_on_cache[c].append(v)
                cache[c] += s_videos[v]

                avglist = []
                for eid in range(n_end):
                    if c2e[c][eid] and v2e[v][eid]:
                        avglist.append(diff_lat[eid][c])

                benefit = np.mean(avglist)

                if benefit == 0:
                    done = True

                update(c, v, benefit)
                found = True
                break

        # check if all caches full

        if not found:
            break

        iter += 1

    return cache, videos_on_cache
