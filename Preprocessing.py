import numpy as np
from sklearn.cluster import MeanShift


def preprocessing(graph):
    c_points = np.zeros(shape=(len(graph['caches']), len(graph['endpoints'])), dtype=np.bool)
    # cluster caches
    for i, c in enumerate(graph['caches']):
        for e in c['endpoints']:
            c_points[i][e] = 1

    ms = MeanShift().fit(c_points)
    print("***", "MEANSHIFT", "***")
    print(len(ms.cluster_centers_))
    print(ms.labels_)
    print("")
