import numpy as np
from sklearn.cluster import MeanShift

from tqdm import tqdm

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
    print(unique_count, "out of", cache_count, "are unique.")

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

    return graph, unique_count < cache_count


def postprocessing(videos_on_cache, cache_mapping, videos, cache_size, video_sizes):
    # greedy unpacking from clusters into caches
    voc_unpacked = [[] for _ in cache_mapping]

    # iterate over all cache-clusters
    for cluster_idx, cluster_cache in tqdm(enumerate(videos_on_cache), desc="Cluster unpacking"):
        # find all caches in the cluster
        caches_in_cluster = []
        for cache_index, cluster_index in enumerate(cache_mapping):
            if cluster_index == cluster_idx:
                caches_in_cluster.append(cache_index)

        # preprocess data
        video_tuples = []
        for video_index in cluster_cache:
            video_tuples.append((video_index, video_sizes[video_index]))

        # sorting is optional, works both ways...
        # d = sorted(d, key=lambda x: -x[1])

        unpacked_cluster = [[] for _ in range(len(caches_in_cluster))]
        size_values = [0] * len(caches_in_cluster)
        for k, video_index in video_tuples:
            packed = False
            for j in range(len(size_values)):
                if size_values[j] + video_index <= cache_size:
                    unpacked_cluster[j].append(k)
                    size_values[j] += video_index
                    packed = True
                    break
            if not packed:
                print("Bin packing failed for video {0}".format(k))

        # add unpacked caches to result
        for k, c___ in enumerate(caches_in_cluster):
            voc_unpacked[c___].extend(unpacked_cluster[k])

    print("Unpacking done")
    return voc_unpacked
