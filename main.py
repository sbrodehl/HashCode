import argparse
import time

from Preprocessing import preprocessing
from best_solution_in_the_wuuuuuuurld import *

parser = argparse.ArgumentParser()

# need to be
parser.add_argument("input", help="input file")
parser.add_argument("output", help="output file")
args = parser.parse_args()

print(args)
start = time.time()

n_vid, n_end, n_req, n_cache, s_cache, s_videos, endpoints, requests = read_dataset(args.input)
graph = build_graph(n_vid, n_end, n_req, n_cache, s_cache, s_videos, endpoints, requests)

graph2 = preprocessing(graph)

tqdm.write("Setup in {0:.2f}s".format((time.time() - start)))

sleep(0.1)

videos_on_cache = solution(graph)

write_solution(args.output, videos_on_cache)

end = time.time()
sleep(0.1)
score = compute_solution_score(videos_on_cache, requests, endpoints)
print("Score {0} in {1:.2f}s".format(score, (end - start)))
