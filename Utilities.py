import sys
import numpy as np
import pandas as pd
from tqdm import tqdm

from collections import namedtuple


def csv_print(mat):
    np.savetxt(sys.stdout.buffer, mat, fmt='%.5f', newline="\n")

Endpoint = namedtuple('Endpoint', ['id', 'lat', 'con'])
Request  = namedtuple('Request', ['vid', 'eid', 'n'])
Scoring = namedtuple('Scoring', ['vid', 'cid', 'score'])


def sort_array_with_id(arr):
    """
    Sort array ascending and keep track of ids.
    :param arr: array with values
    :return: array with tuples (id, val)
    """
    tuple_arr = [(id, arr[id]) for id in range(len(arr))]
    return sorted(tuple_arr, key=lambda t: t[1])

def check_vid_size(cachesize, videosizes):
    for v in videosizes:
        if cachesize < v:
            print('moo')

