import numpy as np
from graphviz import Graph, nohtml
import operator
import seaborn as sns
from objects import Shelf
import matplotlib.pyplot as plt
import os


def get_dirs_in_path(path):
    '''Returns directories in path.'''
    dirs = [os.path.join(path, file) for file in os.listdir(path) if os.path.isdir(os.path.join(path, file))]
    return dirs

def _line_special_cases(x1, y1, x2, y2, dx, dy):
    # Check zero length
    if (x1, y1) == (x2, y2):
        return [(x1, y1)]

    # Check horizontal
    if y1 == y2:
        direction = int(np.sign(x2 - x1))
        return [(x, y1) for x in range(x1, x2 + direction, direction)]

    # Check vertical
    if x1 == x2:
        direction = int(np.sign(y2 - y1))
        return [(x1, y) for y in range(y1, y2 + direction, direction)]

    # Check diagonal
    if abs(dx) == abs(dy):
        diagonal_points = [(x1 + i * np.sign(dx),
                            y1 + i * np.sign(dy))
                           for i in range(abs(dx) + 1)]
        return diagonal_points

    return None


def get_line(start, end):
    # Setup initial conditions
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1

    # Check special cases
    cells = _line_special_cases(x1, y1, x2, y2, dx, dy)
    if cells is not None:
        return cells

    # Determine how steep the line is
    is_steep = abs(dy) > abs(dx)

    # Rotate line
    if is_steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    # Swap start and end points if necessary and store swap state
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True

    # Recalculate differentials
    dx = x2 - x1
    dy = y2 - y1

    # Setup needed variables for the line algorithm
    # Calculate numerator and denominator to avoid floating point issues
    y_numerator = -2 * dy * (2 * x1 + 1) + 2 * dx * (1 + 2 * y1)
    y_denominator = 4 * dx
    not_done = True
    cells = []
    y_direction = int(np.sign(dy / dx))
    prev_cell = (x1, y1)

    # Calculate the cells in the line
    while not_done:
        cells.append(prev_cell)
        next_y = prev_cell[1]
        if y_direction > 0:
            next_y += 1
        next_x = (y_denominator * next_y - y_numerator) * dx / (y_denominator * dy)
        corner_case = next_x.is_integer()
        next_x = int(np.floor(next_x))
        end_addition = 1
        if corner_case:
            end_addition = 0
        for x in range(prev_cell[0] + 1, next_x + end_addition):
            cells.append((x, prev_cell[1]))
            if x == x2:
                not_done = False
                break
        if y_direction < 0:
            next_y -= 1
        prev_cell = (next_x, next_y)

    # Reverse the list if the coordinates were swapped
    if swapped:
        cells.reverse()
    if is_steep:
        for i in range(len(cells)):
            cells[i] = tuple(reversed(cells[i]))
    return cells


def get_neighborhood_str(neighborhood):
    str = ''
    for i in reversed(range(len(neighborhood[0]))):
        row = ''
        for j in range(len(neighborhood[0])):
            row += neighborhood[j][i]
        str += row + '\n'
    return str


def create_graphs(discriminator, memory, format='png'):
    def create_node(g, i, node):
        if node not in memory.mf_dict:
            best_forms = []
        else:
            forms = [x for x in memory.mf_dict[node].items()]
            forms.sort(key=operator.itemgetter(1), reverse=True)
            best_forms = []
            best_score = forms[0][1]
            while len(forms) > 0 and forms[0][1] == best_score:
                best_forms.append(forms.pop(0))
        form_counts = ['{} {}/{}'.format(x[0], memory.meaning_stats[node]['use_counts'][x[0]], x[1])
                       if x[0] in memory.meaning_stats[node]['use_counts']
                       else '{} {}/{}'.format(x[0], 0, x[1])
                       for x in best_forms]
        form = ', '.join(form_counts)
        g.node(str(i), nohtml('{} {}'.format(form, node.range)))

    graphs = []

    for disc_tree in discriminator.trees:
        g = Graph('g', node_attr={'shape': 'record', 'height': '.1'}, format=format)

        i = 0
        nodes = [(disc_tree.root, i)]
        create_node(g, i, disc_tree.root)
        # g.node(str(i), nohtml(str(disc_tree.root.range)))
        while len(nodes) > 0:
            child_nodes = []
            for node in nodes:
                if node[0].child1 is not None:
                    i += 1
                    create_node(g, i, node[0].child1)
                    g.edge(str(node[1]), str(i))
                    child_nodes.append((node[0].child1, i))
                if node[0].child2 is not None:
                    i += 1
                    create_node(g, i, node[0].child2)
                    g.edge(str(node[1]), str(i))
                    child_nodes.append((node[0].child2, i))
            nodes = child_nodes

        graphs.append(g)
    return graphs

def create_heatmap(matrix, grid, fname):
    sns.set()

    # Create mask for shelves
    mask = np.zeros((grid.width, grid.height))
    for x, y in [(x, y) for x in range(grid.width) for y in range(grid.height)]:
        if type(grid.grid[x][y]) == Shelf:
            mask[x][y] = 1
    mask = np.rot90(mask)

    hmap = sns.heatmap(matrix, yticklabels=False, xticklabels=False, square=True, cmap='Blues', mask=mask,
                       linewidths=0.1)
    hmap.set_facecolor('Brown')
    fig = hmap.get_figure()
    fig.savefig(fname, bbox_inches='tight')
    plt.close()