import argparse
import time

from best_solution_in_the_wuuuuuuurld import *

parser = argparse.ArgumentParser()

# need to be
parser.add_argument("input", help="input file")
parser.add_argument("output", help="output file")
args = parser.parse_args()

# read input file
settings, m = read_dataset(args.input)

# start timing
start = time.time()

# compute solution
m = solution(m)

# stop timing
end = time.time()

# write solution
write_solution(args.output, m)

score = compute_solution_score(settings, m)
tqdm.write("Score {0:.0f} in {1:.2f}s".format(score, (end - start)))
