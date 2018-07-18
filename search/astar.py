"""A* search.
"""
from search.pq import PQ

import numpy as np

# "Maximum distance" used for f.
MAX_DIST = 100000

# "Maximum" dimensions for the maps, used to derive fast lookups from dictionaries using object hashs.
MAX_DIM = 100000

# Clock wise index differences from a center point, starting from the upper left corner.
clock_wise = [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)]
clock_wise4 = [(-1, 0), (0, 1), (1, 0), (0, -1)]


class SearchNode:

    def __init__(self, pos, prev, g=0, h=0, f=MAX_DIST):
        self.x = pos[0]
        self.y = pos[1]
        self.pos = pos
        self.prev = prev
        self.g = g
        self.h = h
        self.f = f

    def __eq__(self, other):
        if self.pos == other.pos:
            return True
        return False

    def __hash__(self):
        return self.x * MAX_DIM + self.y


def get_neighbors(map, pos, moore=True):
    n_deltas = clock_wise if moore else clock_wise4
    neighbors = []
    for delta in n_deltas:
        new_pos = (pos[0] + delta[0], pos[1] + delta[1])
        if 0 <= new_pos[0] < map.shape[0] and 0 <= new_pos[1] < map.shape[1]:
            # Passable cells are marked as zeros
            if map[new_pos] == 0:
                neighbors.append((pos[0] + delta[0], pos[1] + delta[1]))
    # We could probably shuffle the neighbors to get rid of some deterministic behavior.
    return neighbors


def get_h(pos, start, moore=True):
    if not moore:
        return abs(pos[0] - start[0]) + abs(pos[1] - start[1])
    else:
        return np.sqrt(abs(pos[0] - start[0]) ** 2 + abs(pos[1] - start[1]) ** 2)


def astar(map, start, goal, moore=True):
    """A* search.

    :param numpy.ndarray map: Binary map, where zeros are passable cells.
    :param tuple start: Starting cell's coordinate
    :param tuple goal: Goal cell's coordinate
    :param bool moore: If true, use 8-connected neighborhoods, otherwise use 4-connected neighborhoods.

    :returns:
        Path (including start and goal cells) to the goal cell as a list of cell coordinates. If the goal cannot be
        reached, returns an empty list.
    """

    # Already looked list
    closed = {}
    # Do the usual from goal to start switch for search.
    # (If the agent moves its position, but the goal stays the same,
    # we could use the cached results of the previous search.)
    open = PQ()
    open.add_task(SearchNode(goal, None, f=0), priority=0)
    start_reached = False

    while not start_reached:
        try:
            node = open.pop_task()
            # print("Popped node {} with f={}.".format(node.pos, node.f))
        except KeyError:
            # If KeyError is raised, the open node list is empty and we cannot find a route to the starting node.
            return []

        # Once we pop the starting node, we know we have the shortest path to it.
        if node.pos == start:
            # print("Path to {} found.".format(node.pos))
            path = construct_path(node)
            print(path)
            return path

        for n_pos in get_neighbors(map, node.pos, moore=moore):
            g = node.g + 1
            h = get_h(n_pos, start, moore=moore)
            f = g + h
            new_node = SearchNode(n_pos, node, g=g, h=h, f=f)
            # print("Considering neighbor {} with f={}".format(n_pos, f))
            if n_pos in closed:
                closed_node = closed[n_pos]
                if new_node.f < closed_node.f:
                    del closed[n_pos]
                    open.add_task(new_node, priority=f)
            else:
                open.add_task(new_node, priority=f)

        closed[node.pos] = node


def construct_path(start_node):
    node = start_node
    path = [node.pos]
    while node.prev is not None:
        node = node.prev
        path.append(node.pos)
    return path


if __name__ == "__main__":
    map = np.zeros((10, 10))
    map[3, 3:9] = 1
    map[1:9, 3] = 1
    map[3:5, 8] = 1
    print(map)
    start = (0, 0)
    goal = (9, 9)
    path = astar(map, start, goal, moore=True)
    for p in path:
        map[p] = 2
    print(map)







