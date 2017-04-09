import argparse
import time

from best_solution_in_the_wuuuuuuurld import *
from Utilities import *

parser = argparse.ArgumentParser()

# need to be
parser.add_argument("input", help="input file")
parser.add_argument("output", help="output file")
parser.add_argument("-v", action="store_true", dest="vis", default=False, help="activate visualization")
parser.add_argument("-s", action="store_true", dest="savefig", help="save image of solution")
args = parser.parse_args()

# read input file
d = read_dataset(args.input)

# start timing
start = time.time()

# compute solution
# d = place_routers(d)
# d = place_cables(d)

d = place_routers_randomized(d)

# stop timing
end = time.time()

# write solution
write_solution(args.output, d)

score = compute_solution_score(d)
tqdm.write("Score {0:.0f} in {1:.2f}s".format(score, (end - start)))

# plot graph with coverage
pngfile = None
if args.savefig:
    pngfile = str(args.output)
    pngfile = pngfile.replace(".out", ".png")

plot_with_coverage(d, pngfile, args.vis)
