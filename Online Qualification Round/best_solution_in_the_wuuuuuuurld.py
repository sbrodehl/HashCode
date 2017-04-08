from heapq import *
from IO import *


def solution(graph):
    caches_count = len(graph['caches'])
    # solutions
    videos_on_cache = [[] for _ in range(caches_count)]
    scores = {}

    ScoreKey = namedtuple('ScoreKey', ['video', 'cache'])

    for cid in tqdm(range(caches_count), desc="Computing Scores"):
        scores_for_c = {}
        cache = graph['caches'][cid]
        # if there are requests, compute score
        for eid in cache['endpoints']:
            ep = graph['endpoints'][eid]
            lat_diff = ep['latency']
            for con in ep['connections']:
                if graph['cache_mapping'][con[0]] == cid:
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

    # update from here on
    pbar = tqdm(total=len(pq), desc="Progressing Priority Queue")
    while pq:
        (s, v, c) = heappop(pq)
        key = ScoreKey(v, c)
        # check if score has changed
        # push the tuple if score has changed
        if scores[key] > s:
            heappush(pq, (scores[key], v, c))
            continue

        pbar.update(1)
        cache_size = np.sum([graph['videos'][vids]['size'] for vids in videos_on_cache[c]])
        if cache_size + graph['videos'][v]['size'] > graph['caches'][c]['size']:
            # continue if cache is full
            continue

        if v in videos_on_cache[c]:
            print("ERROR", "Duplicate video index", v, "in", c)
            break

        videos_on_cache[c].append(v)

        # now update neighboring cache which need to hold the same video
        cache = graph['caches'][c]
        for eid in cache['endpoints']:
            ep = graph['endpoints'][eid]
            for ncon in ep['connections']:
                nc = graph['cache_mapping'][ncon[0]]
                if nc == c:
                    continue
                other = ScoreKey(v, nc)
                if other in scores:

                    lat_diff = ep['latency']
                    for con in ep['connections']:
                        if graph['cache_mapping'][con[0]] == nc:
                            lat_diff -= con[1]
                            break

                    n_requests = 0
                    for rid in graph['videos'][v]['requests']:
                        req = graph['requests'][rid]
                        if req.eid == eid:
                            n_requests = req.n
                            break

                    score = scores[other]
                    score += n_requests * lat_diff / graph['videos'][v]['size']
                    scores[other] = score

    return videos_on_cache
