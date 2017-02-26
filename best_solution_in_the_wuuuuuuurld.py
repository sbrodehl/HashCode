from heapq import *
from time import gmtime, strftime, sleep

from IO import *


def cache_to_endpoint(n_cache, endpoints):
    res = np.zeros(shape=(n_cache, len(endpoints)), dtype=np.bool)

    for ep in endpoints:
        for c in ep.con:
            res[c[0]][ep.id] = True

    return res


def vid_to_endpoint(n_vid, n_end, requests):
    res = np.zeros(shape=(n_vid, n_end), dtype=np.uint32)

    for r in requests:
        res[r.vid][r.eid] = r.n

    return res


def solution(graph, max_iter=3000):
    # solutions
    videos_on_cache = [[] for _ in range(graph['n_caches'])]
    scores = {}

    ScoreKey = namedtuple('ScoreKey', ['video', 'cache'])

    for cid in tqdm(range(graph['n_caches']), desc="Computing Scores"):
        scores_for_c = {}
        cache = graph['caches'][cid]
        # if there are requests, compute score
        for eid in cache['endpoints']:
            ep = graph['endpoints'][eid]
            lat_diff = ep['latency']
            for con in ep['connections']:
                if con[0] == cid:
                    lat_diff -= con[1]
                    break

            for rid in ep['requests']:
                req = graph['requests'][rid]
                key = ScoreKey(req.vid, cid)
                score = 0.0
                if key in scores_for_c:
                    score = scores_for_c[key]
                score -= req.n * lat_diff / graph['videos'][req.vid]['size']
                scores_for_c[key] = score

                del req
                del key
                del score

            del ep

        scores.update(scores_for_c)

        del scores_for_c
        del cache

    pq = []
    for k in tqdm(scores, desc="Filling Priority Queue"):
        heappush(pq, (scores[k], k.video, k.cache))

    # now we have the heap with the scores
    # print("Size of the heap", len(pq), "/", str(len(graph['videos']) * len(graph['caches'])))

    iters = 0
    # update from here on
    pbar = tqdm(total=len(pq), desc="Progressing Priority Queue")
    while pq:
        (s, v, c) = heappop(pq)
        key = ScoreKey(v, c)
        # check if score has changed
        # push the tuple if score has changed
        if scores[key] > s:
            heappush(pq, (scores[key], v, c))

        cache_size = np.sum([graph['videos'][vids]['size'] for vids in videos_on_cache[c]])
        if cache_size + graph['videos'][v]['size'] > graph['max_cache_size']:
            # continue if cache is full
            continue

        videos_on_cache[c].append(v)

        # now update neighboring cache which need to hold the same video
        cache = graph['caches'][c]
        for eid in cache['endpoints']:
            ep = graph['endpoints'][eid]
            for nc in ep['connections']:
                key = ScoreKey(v, nc)
                if key in scores:
                    lat_diff = ep['latency']
                    for con in ep['connections']:
                        if con[0] == nc:
                            lat_diff -= con[1]
                            break
                    n_requests = 0
                    for req in graph['videos'][v]['requests']:
                        if req.eid == eid:
                            n_requests = req.n
                            break

                    score = scores[key]
                    score += n_requests * lat_diff / graph['videos'][v]['size']
                    scores[key] = score

        pbar.update(1)
        iters += 1
        if iters > max_iter:
            break

    return videos_on_cache


def solution_old(n_vid, n_end, n_req, n_cache, s_cache, s_videos, endpoints, requests):
    # solutions
    cache = np.zeros(n_cache)
    videos_on_cache = [[] for _ in range(n_cache)]
    # compute scores
    scores = np.zeros(shape=(n_vid, n_cache), dtype=np.double)
    in_q = np.zeros(shape=(n_vid, n_cache), dtype=np.double)

    pq = []

    c2e = cache_to_endpoint(n_cache, endpoints)
    v2e = vid_to_endpoint(n_vid, n_end, requests)

    for req in tqdm(requests, desc="Computing scores for Video/Cache Pairs"):
        ep = endpoints[req.eid]
        for c in ep.con:
            d_latency = ep.lat - c[1]
            score = req.n * d_latency * (1.0 / s_videos[req.vid])
            scores[req.vid][c[0]] -= score

    for req in tqdm(requests, desc="Pushing Video/Cache Pairs into Priority Queue"):
        ep = endpoints[req.eid]
        for c in ep.con:
            if not in_q[req.vid][c[0]]:
                in_q[req.vid][c[0]] = True
                heappush(pq, (scores[req.vid][c[0]], req.vid, c[0]))

    tqdm.write(str(100 * (len(pq)) / (n_vid * n_cache)) + "% in Queue.")
    sleep(0.1)
    pbar = tqdm(total=len(pq), desc="Progressing Priority Queue")
    # update from here on
    while pq:
        pbar.update(1)
        (s, v, c) = heappop(pq)

        # check if score has changed
        if any(v in cache_ for cache_ in videos_on_cache):
            if scores[v][c] > s:
                heappush(pq, (scores[v][c], v, c))

        if cache[c] + s_videos[v] <= s_cache:
            videos_on_cache[c].append(v)
            cache[c] += s_videos[v]

            if not True:
                # update scores for connected caches / videos
                for req in requests:
                    if req.vid == v:
                        ep = endpoints[req.eid]
                        for ca in ep.con:
                            d_latency = ep.lat - ca[1]
                            score = v2e[v][req.eid] * d_latency * (1.0 / s_videos[v])
                            # is this the right one?
                            scores[v][ca[0]] = 0  # score
            else:
                # update scores for connected caches / videos
                for eid in range(n_end):
                    # endpoint connects to cache
                    if c2e[c][eid]:
                        # if video is requested by the endpoint
                        if v2e[v][eid]:
                            ep = endpoints[eid]
                            for ec in ep.con:
                                d_latency = ep.lat - ec[1]
                                score = v2e[v][eid] * d_latency * (1.0 / s_videos[v])
                                scores[v][ec[0]] = 0  # score

        if len(pq) % 1000 == 0:
            write_solution(strftime("%Y%m%d-%H%M%S", gmtime()), cache, videos_on_cache)

    return cache, videos_on_cache
