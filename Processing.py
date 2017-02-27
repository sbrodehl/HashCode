import numpy as np
from sklearn.cluster import MeanShift


def unique_rows(a):
    a = np.ascontiguousarray(a)
    unique_a = np.unique(a.view([('', a.dtype)]*a.shape[1]))
    return unique_a.view(a.dtype).reshape((unique_a.shape[0], a.shape[1]))


def preprocessing(graph):
    cache_count = len(graph['caches'])
    c_points = np.zeros(shape=(cache_count, len(graph['endpoints'])), dtype=np.bool)
    # cluster caches
    for i, c in enumerate(graph['caches']):
        for e in c['endpoints']:
            c_points[i][e] = 1

    # ms = MeanShift().fit(c_points)
    # print("***", "MEANSHIFT", "***")
    # print(len(ms.cluster_centers_))
    # print(ms.labels_)

    uniques = unique_rows(c_points)
    uniques = [tuple(row) for row in uniques]
    unique_count = len(uniques)
    print("***", "UNIQUES", "***")
    print(unique_count, "of", cache_count, "=", str(100*unique_count/cache_count) + "%")

    cache_mapping = np.zeros(cache_count, dtype=np.int)
    for i in range(cache_count):
        cache_mapping[i] = i

    if unique_count < cache_count:

        caches_old = graph['caches']
        caches = [{'endpoints': [], 'size': 0} for _ in range(unique_count)]

        # now join clusters
        for i, c in enumerate(c_points):
            index = uniques.index(tuple(c))
            cache_mapping[i] = index
            caches[index]['size'] += caches_old[i]['size']
            caches[index]['endpoints'] = caches_old[i]['endpoints']

        graph['caches'] = caches

    graph['cache_mapping'] = cache_mapping

    return graph


def postprocessing(videos_on_cache, cache_mapping, videos):
    # split the unique caches
    return videos_on_cache
