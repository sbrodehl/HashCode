import os
import argparse
import time

from best_solution_in_the_wuuuuuuurld import *
from Utilities import *

avail_methods = [
    'rand',
    'conv',
    'skel'
]

parser = argparse.ArgumentParser()

# need to be
parser.add_argument("input", help="input file")
parser.add_argument("output", help="output file")
parser.add_argument("-v", action="store_true", dest="vis", default=False, help="activate visualization")
parser.add_argument("-s", action="store_true", dest="savefig", help="save image of solution")
parser.add_argument('-m', choices=avail_methods, dest="method", required=True)
args = parser.parse_args()

# read input file
d = read_dataset(args.input)

# start timing
start = time.time()

if args.method == 'rand':
    d = place_routers_randomized(d)
elif args.method == 'conv':
    d = place_routers_by_convolution(d)
elif args.method == 'skel':
    d = place_routers_on_skeleton_iterative(d)
else:
    raise Exception('No such method!')

# stop timing
end = time.time()

# output filepath magic
fname, fext = os.path.splitext(args.output)
meth_str = "." + args.method
# write solution
write_solution(fname + meth_str + fext, d)

score = compute_solution_score(d)
tqdm.write("Score {0:.0f} in {1:.2f}s".format(score, (end - start)))

# plot graph with coverage
pngfile = None
if args.savefig:
    pngfile = str(args.output)
    pngfile = pngfile.replace(fext, meth_str + ".png")

plot_with_coverage(d, pngfile, args.vis)
