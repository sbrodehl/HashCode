import argparse
import time

from Processing import preprocessing, postprocessing
from best_solution_in_the_wuuuuuuurld import *

parser = argparse.ArgumentParser()

# need to be
parser.add_argument("input", help="input file")
parser.add_argument("output", help="output file")
args = parser.parse_args()

dataset = read_dataset(args.input)

start = time.time()

graph = build_graph(dataset)
graph2 = preprocessing(graph)

tqdm.write("Overall setup in {0:.2f}s".format((time.time() - start)))

solution = postprocessing(graph2)

end = time.time()

write_solution(args.output, solution)

score = compute_solution_score(solution)
tqdm.write("Score {0:.0f} in {1:.2f}s".format(score, (end - start)))
