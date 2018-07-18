import numpy as np


def build_map(grid, impassable_contents):
    """Build numpy array from Mesa's space.Grid.

    :param grid: Mesa's space.Grid
    :param impassable_contents: Object types which are impassable for the agent.
    """
    grid_map = np.zeros((grid.height, grid.width))

    for cont, x, y in grid.coord_iter():
        if type(cont) in impassable_contents:
            grid_map[x, y] = 1

    return grid_map

