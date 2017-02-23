import sys
import numpy as np
import pandas as pd
from tqdm import tqdm

from collections import namedtuple


def csv_print(mat):
    np.savetxt(sys.stdout.buffer, mat, fmt='%.5f', newline="\n")

Endpoint = namedtuple('Endpoint', ['id', 'lat', 'con'])
Request  = namedtuple('Request', ['vid', 'eid', 'n'])
