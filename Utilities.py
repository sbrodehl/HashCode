import sys
import numpy as np
import pandas as pd
from tqdm import tqdm


def csv_print(mat):
    np.savetxt(sys.stdout.buffer, mat, fmt='%.5f', newline="\n")
