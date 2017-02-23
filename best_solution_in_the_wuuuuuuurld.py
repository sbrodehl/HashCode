import numpy as np
from tqdm import tqdm

from Utilities import Scoring


def solution(n_vid, n_end, n_req, n_cache, s_cache, s_videos, endpoints, requests):

    scores = np.zeros(shape=(n_vid, n_cache), dtype=np.double)
    tscores = []
    for ep in tqdm(range(n_req)):
        req = requests[ep]
        vid_size = s_videos[req.vid]
        r_vid_size = 1.0 / vid_size
        ep = endpoints[req.eid]
        for c in ep.con:
            d_latency = ep.lat - c[1]
            score = req.n * d_latency * r_vid_size
            scores[req.vid][c[0]] += score

    for v in range(n_vid):
        for c in range(n_cache):
            tscores.append(Scoring(v, c, scores[v][c]))

    s_scores = sorted(tscores, key=lambda x: x[0])

    cache = np.zeros(n_cache)
    videos_on_cache = [[] for _ in range(n_cache)]
    for t in s_scores:
        c = t.cid
        v = t.vid
        s = t.score
        if cache[c] + s_videos[v] <= s_cache:
            videos_on_cache[c].append(v)
            cache[c] += s_videos[v]

    return cache, videos_on_cache
