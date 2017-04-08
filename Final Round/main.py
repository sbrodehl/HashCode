import argparse
import time

from best_solution_in_the_wuuuuuuurld import *

parser = argparse.ArgumentParser()

# need to be
parser.add_argument("input", help="input file")
parser.add_argument("output", help="output file")
args = parser.parse_args()

# read input file
d = read_dataset(args.input)

# start timing
start = time.time()

# compute solution
d = solution(d)

# stop timing
end = time.time()

# write solution
write_solution(args.output, d)

score = compute_solution_score(d)
tqdm.write("Score {0:.0f} in {1:.2f}s".format(score, (end - start)))
