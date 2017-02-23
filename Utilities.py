import sys
import numpy as np

from collections import namedtuple

Endpoint = namedtuple('Endpoint', ['id', 'lat', 'con'])
Request = namedtuple('Request', ['vid', 'eid', 'n'])
Scoring = namedtuple('Scoring', ['vid', 'cid', 'score'])


def csv_print(mat, fmt="%.5f"):
    np.savetxt(sys.stdout.buffer, mat, fmt=fmt, newline="\n")


def sort_array_with_id(arr):
    """
    Sort array ascending and keep track of ids.
    :param arr: array with values
    :return: array with tuples (id, val)
    """
    tuple_arr = [(id, arr[id]) for id in range(len(arr))]
    sorted(tuple_arr, key=lambda t: t[1])
    return tuple_arr
