import argparse
import time

from best_solution_in_the_wuuuuuuurld import *
from Utilities import *

parser = argparse.ArgumentParser()

# need to be
parser.add_argument("input", help="input file")
parser.add_argument("output", help="output file")
parser.add_argument("-v", action="store_true", dest="vis", help="activate visualization")
args = parser.parse_args()

# read input file
d = read_dataset(args.input)

# start timing
start = time.time()

# compute solution
# d = place_routers(d)
# d = place_cables(d)

d = place_many_routers(d)

# stop timing
end = time.time()

# write solution
write_solution(args.output, d)

score = compute_solution_score(d)
tqdm.write("Score {0:.0f} in {1:.2f}s".format(score, (end - start)))

if args.vis:
    pngfile = str(args.output)
    pngfile = pngfile.replace(".out", ".png")
    skel, pos = compute_skel(d)
    # plot_graph_with_skeleton(d, skel)

    # plot graph with coverage
    fig = plt.figure()

    plt.imshow(d['graph'], cmap=plt.cm.viridis, interpolation='none')
    plt.axis('off')
    # plt.set_title('original', fontsize=20)

    routers = []
    g = d['graph']
    for x, row in enumerate(g):
        for y, val in enumerate(row):
            if val == Cell.ConnectedRouter:
                routers.append((x, y))

    coverage = np.zeros((d['height'], d['width']), dtype=np.bool)
    R = d['radius']
    for r in range(len(routers)):
        a, b = routers[r]
        mask = wireless_access(a, b, d)
        coverage[(a - R):(a + R + 1), (b - R):(b + R + 1)] |= mask.astype(np.bool)

    plt.imshow(coverage, cmap=plt.cm.gray, alpha=0.2, interpolation='none')
    plt.savefig('output.png')
    plt.show()

    # fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(8, 4),
    #                          sharex=True, sharey=True,
    #                          subplot_kw={'adjustable': 'box-forced'})
    #
    # ax = axes.ravel()
    #
    # ax[0].imshow(d['graph'], cmap=plt.cm.gray)
    # ax[0].axis('off')
    # ax[0].set_title('original', fontsize=20)
    #
    # ax[1].imshow(d['graph'])
    # ax[1].axis('off')
    # ax[1].set_title('skeleton', fontsize=20)
    #
    # fig.tight_layout()
    # plt.show()


