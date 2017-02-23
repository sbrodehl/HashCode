import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')

import numpy as np
import pandas as pd
import argparse

from Utilities import *

parser = argparse.ArgumentParser()

# need to be
parser.add_argument("A", help="first matrix")
parser.add_argument("B", help="second matrix")
# optional
parser.add_argument("--output", help="path for diff matrix")

args = parser.parse_args()

print(args.A)
print(args.B)
