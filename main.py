import numpy as np
import pandas as pd
import argparse
from tqdm import tqdm

from Utilities import *
from IO import *
from best_solution_in_the_wuuuuuuurld import *

parser = argparse.ArgumentParser()

# need to be
parser.add_argument("input", help="input file")
parser.add_argument("output", help="output file")
args = parser.parse_args()

print(args.input)

n_vid, n_end, n_req, n_cache, s_cache, s_videos, endpoints, requests = read_dataset(args.input)

cache, videos_on_cache = solution(n_vid, n_end, n_req, n_cache, s_cache, s_videos, endpoints, requests)

write_solution(args.output, cache, videos_on_cache)
