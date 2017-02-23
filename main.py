import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')

import numpy as np
import pandas as pd
import argparse

from Utilities import *
from IO import *

parser = argparse.ArgumentParser()

# need to be
parser.add_argument("input", help="input file")
args = parser.parse_args()

print(args.input)
read_dataset(args.input)
