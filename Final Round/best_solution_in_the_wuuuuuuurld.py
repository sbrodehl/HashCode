from random import shuffle

from skimage.morphology import skeletonize, medial_axis
from tqdm import tqdm
from scipy import signal
import scipy.ndimage.filters as fi
import pickle
import glob
import bz2
import multiprocessing
from multiprocessing import Pool
from functools import partial
from IO import *
from Utilities import compute_solution_score, wireless_access, quasi_euclidean_dist, chessboard_dist
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree


def place_routers_on_skeleton(d, cmethod):
    wireless = np.where(d["graph"] == Cell.Wireless, 1, 0)
    # perform skeletonization
    skeleton = skeletonize(wireless)
    med_axis = medial_axis(wireless)

    skel = skeleton
    # skel = med_axis
    # get all skeleton positions
    pos = []
    for i in range(skel.shape[0]):
        for j in range(skel.shape[1]):
            if skel[i][j]:
                pos.append((i, j))

    budget = d['budget']
    shuffle(pos)

    max_num_routers = min([int(d['budget'] / d['price_router']), len(pos)])
    print("Num of routers constrained by:")
    print(" budget:   %d" % int(int(d['budget'] / d['price_router'])))
    print(" skeleton: %d" % len(pos))

    for i in tqdm(range(max_num_routers), desc="Placing Routers"):
        new_router = pos[i]
        a, b = new_router

        # check if remaining budget is enough
        d["graph"][a][b] = Cell.Router
        d, ret, cost = _add_cabel(d, new_router, budget)
        budget -= cost

        if not ret:
            break

    return d


def place_routers_on_skeleton_iterative(d, cmethod):
    budget = d['budget']
    R = d['radius']
    max_num_routers = int(d['budget'] / d['price_router'])
    coverage = np.where(d["graph"] == Cell.Wireless, 1, 0).astype(np.bool)

    pbar = tqdm(range(max_num_routers), desc="Placing Routers")
    while budget > 0:
        # perform skeletonization
        # skeleton = skeletonize(coverage)
        skeleton = medial_axis(coverage)
        # get all skeleton positions
        pos = np.argwhere(skeleton > 0).tolist()
        # escape if no positions left
        if not len(pos):
            break
        # get a random position
        shuffle(pos)
        a, b = pos[0]
        # place router
        d["graph"][a][b] = Cell.Router
        d, ret, cost = _add_cabel(d, (a, b), budget)
        if not ret:
            print("No budget available!")
            break
        budget -= cost
        # refresh wireless map by removing new coverage
        m = wireless_access(a, b, R, d['graph']).astype(np.bool)
        coverage[(a - R):(a + R + 1), (b - R):(b + R + 1)] &= ~m
        pbar.update()
    pbar.close()

    return d


def place_routers_randomized(d, cmethod):
    max_num_routers = int(d['budget'] / d['price_router'])
    wireless = np.where(d["graph"] == Cell.Wireless, 0, 1)

    print("Num of routers constrained by:")
    print(" budget:   %d" % int(int(d['budget'] / d['price_router'])))
    budget = d['budget']
    R = d['radius']

    if cmethod == 'mst':
        cost, succ, routers, idx, idy, dists = _mst(d, d['backbone'])

    pbar = tqdm(range(max_num_routers), desc="Placing Routers")
    for i in pbar:
        # generate random position for router
        indices = np.argwhere(wireless == 0).tolist()
        x, y = indices[np.random.randint(0, len(indices))]

        if len(indices) == 0:
            pbar.close()
            print("No more suitable positions left!")
            return d

        # modify graph
        if cmethod == 'bfs':
            d["graph"][x][y] = Cell.Router
            d, ret, cost = _add_cabel(d, (x, y), budget)

            if ret:
                budget -= cost

                # refresh wireless map by removing new coverage
                mask = wireless_access(x, y, R, d['graph'])
                wireless[(x - R):(x + R + 1), (y - R):(y + R + 1)] |= mask.astype(np.bool)
            else:
                # no more budget left
                pbar.close()
                print("No budget available!")
                return d
        elif cmethod == 'mst':
            tmp = d["graph"][x][y]
            d["graph"][x][y] = Cell.Router
            cost, succ, routers, idx, idy, dists = _mst(d, (x, y), routers, idx, idy, dists)

            if succ and i < 10:
                mask = wireless_access(x, y, R, d['graph'])
                wireless[(x - R):(x + R + 1), (y - R):(y + R + 1)] |= mask.astype(np.bool)
            else:
                # reverse last router
                d["graph"][x][y] = tmp
                d = _place_mst_paths(d, routers, idx, idy, dists)
                pbar.close()
                print("No budget available!")
                return d

    pbar.update(max_num_routers)
    return d


def _parallel_helper(position, radius, graph, offset=(0, 0)):
    a, b = position
    ux_min, uy_min = offset
    a, b = a + ux_min, b + uy_min
    mask = wireless_access(a, b, radius, graph)
    return a, b, np.sum(np.nan_to_num(mask)), mask


def _parallel_counting_helper(position, radius, graph, scoring, offset=(0, 0)):
    a, b = position
    ux_min, uy_min = offset
    a, b = a + ux_min, b + uy_min

    mask = wireless_access(a, b, radius, graph)

    wx_min, wx_max = np.max([0, (a - radius)]), np.min([scoring.shape[0], (a + radius + 1)])
    wy_min, wy_max = np.max([0, (b - radius)]), np.min([scoring.shape[1], (b + radius + 1)])
    # get the submask which is valid
    dx, lx = np.abs(wx_min - (a - radius)), wx_max - wx_min
    dy, ly = np.abs(wy_min - (b - radius)), wy_max - wy_min

    return a, b, np.sum(np.multiply(scoring[wx_min:wx_max, wy_min:wy_max], np.nan_to_num(mask[dx:dx + lx, dy:dy + ly])))


def place_routers_randomized_by_score(d, cmethod):
    # some constants
    max_num_routers = int(d['budget'] / d['price_router'])
    budget = d['budget']
    R = d['radius']
    wireless = np.where(d["graph"] == Cell.Wireless, 1, 0).astype(np.int8)
    scoring = np.zeros(wireless.shape, dtype=np.float32) - 1
    counting = np.zeros_like(scoring)
    coverage = {}

    print("Num of routers constrained by:")
    print(" budget:   %d" % max_num_routers)

    fscore = d['name'] + ".scores"
    fcov = d['name'] + ".coverage"
    facc = d['name'] + ".counting"

    compute_stuff = False

    sample_files = glob.glob('output/' + facc)
    if len(sample_files) and not compute_stuff:
        print("Found accounting file.")
        counting = pickle.load(bz2.BZ2File(sample_files[0], 'r'))
    else:
        compute_stuff = True

    sample_files = glob.glob('output/' + fscore)
    if len(sample_files) and not compute_stuff:
        print("Found scoring file.")
        scoring = pickle.load(bz2.BZ2File(sample_files[0], 'r'))
    else:
        compute_stuff = True

    sample_files = glob.glob('output/' + fcov)
    if len(sample_files) and not compute_stuff:
        print("Found coverage file.")
        coverage = pickle.load(bz2.BZ2File(sample_files[0], 'r'))
    else:
        compute_stuff = True

    if compute_stuff:
        # compute initial scoring, which will be updated during placing
        positions = np.argwhere(wireless > 0).tolist()
        # start worker processes
        with Pool(processes=multiprocessing.cpu_count()) as pool:
            for a, b, s, m in pool.imap_unordered(partial(_parallel_helper, radius=R, graph=d['original']), positions):
                scoring[a][b] = s
                coverage[(a, b)] = m
        # start worker processes
        with Pool(processes=multiprocessing.cpu_count()) as pool:
            for a, b, s in pool.imap_unordered(
                    partial(_parallel_counting_helper, radius=R, graph=wireless, scoring=scoring), positions):
                counting[a][b] = s

        print("Saving scoring file.")
        # save scoring to disk
        pickle.dump(scoring, bz2.BZ2File('output/' + fscore, 'w'), pickle.HIGHEST_PROTOCOL)
        print("Saving coverage file.")
        # save coverage to disk
        pickle.dump(coverage, bz2.BZ2File('output/' + fcov, 'w'), pickle.HIGHEST_PROTOCOL)
        print("Saving counting file.")
        # save coverage to disk
        pickle.dump(counting, bz2.BZ2File('output/' + facc, 'w'), pickle.HIGHEST_PROTOCOL)

    routers = []
    idx, idy, dists = [], [], []
    if cmethod == 'mst':
        placed, cost, routers, idx, idy, dists = _mst(d, d['backbone'])

    # choose routers by score and place them!
    pbar = tqdm(range(max_num_routers), desc="Placing Routers")
    while budget > 0:
        placement = None
        max_score = scoring.max()
        if max_score > 0:
            possible_placements = np.argwhere(scoring == max_score).tolist()
            score_count = {}
            for pp in possible_placements:
                score_count[(pp[0], pp[1])] = counting[pp[0]][pp[1]]
            sorted_scores = sorted(score_count)
            placement = next(iter(sorted_scores or []), None)

        if placement is None:
            print("No positions available!")
            break

        # update progress bar
        pbar.update()

        x, y = placement

        cost = 0
        placed = False
        if cmethod == 'mst':
            tmp = d["graph"][x][y]
            d["graph"][x][y] = Cell.Router
            placed, nbud, routers, idx, idy, dists = _mst(d, (x, y), routers, idx, idy, dists)
            budget = d['budget'] - nbud
            if not placed:
                d["graph"][x][y] = tmp
                routers = routers[:-1]
                idx, idy, dists = idx[:-len(routers)], idy[:-len(routers)], dists[:-len(routers)]
        else:
            # bfs as default
            # modify graph, add router and cables
            d["graph"][x][y] = Cell.Router
            d, placed, cost = _add_cabel(d, (x, y), budget)

        # check if new path is not to expensive
        if not placed:
            print("No budget available!")
            break

        # update budget
        budget -= cost

        # prepare coverage and scoring for next round
        # remove score for current router

        wx_min, wx_max = np.max([0, (x - R)]), np.min([wireless.shape[0], (x + R + 1)])
        wy_min, wy_max = np.max([0, (y - R)]), np.min([wireless.shape[1], (y + R + 1)])
        # get the submask which is valid
        dx, lx = np.abs(wx_min - (x - R)), wx_max - wx_min
        dy, ly = np.abs(wy_min - (y - R)), wy_max - wy_min

        # remove coverage from map
        wireless[wx_min:wx_max, wy_min:wy_max] &= ~(coverage[(x, y)][dx:dx + lx, dy:dy + ly].astype(np.bool))
        # nullify scores
        scoring[wx_min:wx_max, wy_min:wy_max] = -1

        ux_min, uy_min = np.max([0, (x - 2 * R)]), np.max([0, (y - 2 * R)])
        ux_max, uy_max = np.min([wireless.shape[0], (x + 2 * R + 1)]), np.min([wireless.shape[1], (y + 2 * R + 1)])
        # compute places to be updated
        updating = wireless[ux_min:ux_max, uy_min:uy_max]

        # get all position coordinates
        positions = np.argwhere(updating).tolist()
        # start worker processes
        with Pool(processes=multiprocessing.cpu_count()) as pool:
            for a, b, s, m in pool.imap_unordered(
                    partial(_parallel_helper, radius=R, graph=wireless, offset=(ux_min, uy_min)), positions):
                scoring[a][b] = s
        # start worker processes
        with Pool(processes=multiprocessing.cpu_count()) as pool:
            for a, b, s in pool.imap_unordered(
                    partial(_parallel_counting_helper, radius=R, graph=wireless, scoring=scoring,
                            offset=(ux_min, uy_min)), positions):
                counting[a][b] = s

        counting = np.multiply(counting, wireless)

    # budget looks good, place all cables
    if cmethod == 'mst':
        d = _place_mst_paths(d, routers, idx, idy, dists)

    pbar.close()
    return d


def place_routers_by_convolution(d, cmethod):
    max_num_routers = int(d['budget'] / d['price_router'])
    # wireless = np.where(d["graph"] == Cell.Wireless, 1, 0).astype(np.float64)
    wireless = np.where(d["graph"] == Cell.Wireless, 1, -1).astype(np.float64)
    walls = np.where(d['graph'] <= Cell.Wall, 0, 1).astype(np.float64)

    print("Num of routers constrained by:")
    print(" budget:   %d" % int(int(d['budget'] / d['price_router'])))
    budget = d['budget']
    R = d['radius']
    r21 = 2 * R + 1
    stdev = 6.6

    # kernel = np.ones((2*R+1, 2*R+1))
    # kernel = (_gkern2(2 * R + 1, 2) * 1e2)
    kernel = (np.outer(signal.gaussian(r21, stdev), signal.gaussian(r21, stdev))).astype(np.float32)

    pbar = tqdm(range(max_num_routers), desc="Placing Routers")
    while budget > 0:
        # convolve
        mat = signal.fftconvolve(wireless, kernel, mode='same')

        found = False
        while not found:
            # get the max of the conv matrix
            mat_max = mat.max()
            max_positions = np.argwhere(mat == mat_max).tolist()
            selected_pos = max_positions[np.random.randint(0, len(max_positions))]

            # check if we have suitable positions left
            if mat_max == -np.inf:
                pbar.close()
                print("No more suitable positions left!")
                return d

            x, y = selected_pos

            # max can be on a wall position... ignore it
            if d['graph'][x][y] <= Cell.Wall:
                # pbar.write('> Optimal position on wall cell...')
                mat[x][y] = -np.inf
            else:
                found = True

        # update progress bar
        pbar.update()

        # modify graph
        d["graph"][x][y] = Cell.Router
        d, ret, cost = _add_cabel(d, (x, y), budget)

        # check if new path is not to expensive
        if ret:
            budget -= cost

            # refresh wireless map by removing new coverage
            mask = wireless_access(x, y, R, d['graph'])
            # wireless[(a - R):(a + R + 1), (b - R):(b + R + 1)] &= ~mask.astype(np.bool)
            # wireless[(x - R):(x + R + 1), (y - R):(y + R + 1)] -= kernel
            wireless[(x - R):(x + R + 1), (y - R):(y + R + 1)] = -1.0
        else:
            # we've not enough budget
            pbar.close()
            print("No budget available!")
            return d

    pbar.close()
    return d


def _mst(d, new_router, routers=[], idx=[], idy=[], dists=[]):

    new_id = len(routers)

    # calc new router dists
    for i, a in enumerate(routers):
        dist = chessboard_dist(a, new_router)
        if dist > 0:
            idx.append(i)
            idy.append(new_id)
            dists.append(dist)

    # add new router
    routers.append(new_router)
    # create matrix
    mat = csr_matrix((dists, (idx, idy)), shape=(len(routers), len(routers)))

    # minimal spanning tree
    Tmat = minimum_spanning_tree(mat)

    # check costs
    cost = np.sum(Tmat) * d['price_backbone'] + (len(routers) - 1) * d['price_router']
    succ = cost <= d['original_budget']

    # return
    return succ, cost, routers, idx, idy, dists


def find_chess_connection(a, b):
    cables = []
    dx, dy = np.abs(a[0] - b[0]) + 1, np.abs(a[1] - b[1]) + 1
    xmin, ymin = np.min([a[0], b[0]]), np.min([a[1], b[1]])
    path = np.zeros((dx, dy), dtype=np.bool)
    path[a[0] - xmin][a[1] - ymin] = True
    path[b[0] - xmin][b[1] - ymin] = True
    r = [dx, dy]
    amin = np.argmin(r)

    flipped = False
    if not path[0][0]:
        path = np.flipud(path)
        flipped = True

    # set diagonal elements
    for i in range(r[amin]):
        path[i][i] = True

    # set remaining straight elements
    if amin == 0:
        for i in range(np.abs(dx - dy)):
            path[-1][r[amin] + i] = True
    elif amin == 1:
        for i in range(np.abs(dx - dy)):
            path[r[amin] + i][-1] = True

    if flipped:
        path = np.flipud(path)

    # select cables
    for i, row in enumerate(path):
        for j, col in enumerate(row):
            if path[i][j]:
                cables.append((i + xmin, j + ymin))
    return cables


def find_connection(router_from, router_to):
    cables = []
    if router_from[0] < router_to[0]:
        xr = range(router_from[0], router_to[0] + 1)
    else:
        xr = range(router_from[0], router_to[0] - 1, -1)

    if router_from[1] < router_to[1]:
        yr = range(router_from[1], router_to[1] + 1)
    else:
        yr = range(router_from[1], router_to[1] - 1, -1)

    for x1 in xr:
        cables.append((x1, router_from[1]))

    for y1 in yr:
        cables.append((router_to[0], y1))

    return cables


def _place_mst_paths(d, routers, idx, idy, dists):
    # calc mst
    mat = csr_matrix((dists, (idx, idy)), shape=(len(routers), len(routers)))
    Tmat = minimum_spanning_tree(mat).toarray()

    # place cabels
    for i, r in enumerate(Tmat):
        for j, c in enumerate(r):
            if Tmat[i, j] > 0:
                cables = find_chess_connection(routers[i], routers[j])
                for cable in cables:
                    if cable == d['backbone']:
                        continue
                    if d['graph'][cable] == Cell.Router:
                        d['graph'][cable] = Cell.ConnectedRouter
                    else:
                        d['graph'][cable] = Cell.Cable

    for router in routers:
        if router == d['backbone']:
            continue
        d['graph'][router] = Cell.ConnectedRouter

    return d


def _add_cabel(d, new_router, remaining_budget):
    path = _bfs(d, new_router)
    cost = len(path) * d['price_backbone'] + d['price_router']

    if cost <= remaining_budget:
        for c in path:
            if d['graph'][c] == Cell.Router:
                d['graph'][c] = Cell.ConnectedRouter
            else:
                d['graph'][c] = Cell.Cable

        return d, True, cost

    return d, False, cost


def _bfs(d, start):
    dx = [0, -1, 1]
    dy = [0, -1, 1]

    visited = np.zeros((d['height'], d['width']), dtype=np.bool)
    parent = (np.zeros((d['height'], d['width']), dtype=np.int32) - 1).tolist()

    queue = deque()
    queue.append(start)
    visited[start[0]][start[1]] = True

    while queue:
        cur = queue.popleft()

        # check goal condition
        if d['graph'][cur] >= Cell.ConnectedRouter or cur == d['backbone']:
            # generate path from parent array
            path = []
            a = cur
            while a != start:
                path.append(a)
                a = parent[a[0]][a[1]]
            path.append(a)
            return path[1:]

        # add children
        # check neighbors
        for ddx in dx:
            for ddy in dy:
                if ddx == 0 and ddy == 0:
                    continue

                child_x, child_y = cur[0] + ddx, cur[1] + ddy
                # only if still in the grid
                if 0 <= child_x < d['height'] and 0 <= child_y < d['width']:
                    child = (child_x, child_y)
                    # everything is "walkable" cells
                    if not visited[child[0]][child[1]]:
                        queue.append(child)
                        visited[child[0]][child[1]] = True
                        parent[child[0]][child[1]] = cur

    return None


def _gkern2(kernlen=21, nsig=3):
    """Returns a 2D Gaussian kernel array."""

    # create nxn zeros
    inp = np.zeros((kernlen, kernlen))
    # set element at the middle to one, a dirac delta
    inp[kernlen // 2, kernlen // 2] = 1
    # gaussian-smooth the dirac, resulting in a gaussian filter mask
    return fi.gaussian_filter(inp, nsig)


if __name__ == '__main__':
    D = read_dataset('input/example.in')
    budget = D['budget']
    routers = [(3, 6), (3, 9)]
    for r in routers:
        # set routers
        D['graph'][r[0], r[1]] = Cell.Router
        D, placed, cost = _add_cabel(D, r, budget)
        if not placed:
            print("No budget available!")
            break
        budget -= cost

    score = compute_solution_score(D)
    print(score)
    write_solution('output/example.out', D)
