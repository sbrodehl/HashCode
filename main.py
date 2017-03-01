import argparse
import time

from Processing import preprocessing, postprocessing
from best_solution_in_the_wuuuuuuurld import *

parser = argparse.ArgumentParser()

# need to be
parser.add_argument("input", help="input file")
parser.add_argument("output", help="output file")
args = parser.parse_args()

n_vid, n_end, n_req, n_cache, s_cache, s_videos, endpoints, requests = read_dataset(args.input)

start = time.time()

graph = build_graph(n_vid, n_end, n_req, n_cache, s_cache, s_videos, endpoints, requests)
graph2, uses_clusters = preprocessing(graph)

tqdm.write("Overall setup in {0:.2f}s".format((time.time() - start)))

videos_on_cache = solution(graph2)

if uses_clusters:
    videos_on_cache = postprocessing(videos_on_cache, graph2['cache_mapping'], s_cache, s_videos)

end = time.time()

write_solution(args.output, videos_on_cache)

score = compute_solution_score(videos_on_cache, requests, endpoints)
tqdm.write("Score {0:.0f} in {1:.2f}s".format(score, (end - start)))
