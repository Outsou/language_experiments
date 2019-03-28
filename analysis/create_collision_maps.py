import shutil
import os
from utils import get_dirs_in_path
import ast
from coopa_model import CoopaModel
import numpy as np
import pickle
from objects import Shelf
import seaborn as sns
import matplotlib.pyplot as plt


def get_pickles_in_path(path):
    '''Returns the pickle filepaths in path.'''
    pickles = [os.path.join(path, file) for file in os.listdir(path) if file[-2:] == '.p']
    return pickles

def get_stats(result_path, width, height):
    '''Loads pickles in result path to a dictionary.'''
    collision_map = np.zeros((width, height))
    run_dirs = sorted(get_dirs_in_path(result_path))
    stats = {}
    for run_dir in run_dirs:
        run_id = int(os.path.basename(run_dir))
        # print(run_id)
        stats[run_id] = {}
        pickles = get_pickles_in_path(run_dir)
        for pkl_file in pickles:
            fname = os.path.splitext(os.path.basename(pkl_file))[0]
            if fname.isdigit() or fname in ['blue', 'black', 'green', 'pink', 'purple', 'red']:
                pkl = pickle.load(open(pkl_file, 'rb'))
                stats[run_id][fname] = pkl['collision_map']
                collision_map += pkl['collision_map']
    return collision_map / len(run_dirs)

def gather_collisions(dir, width, height):
    print('Loading collision maps...')
    collision_map = get_stats(dir, width, height)
    print('Done loading...')
    return  collision_map

if __name__ == '__main__':
    result_path = r'D:\resultit\asd'
    analysis_dir = 'coll_maps'
    sns.set()

    shutil.rmtree(analysis_dir, ignore_errors=True)
    print('')
    os.mkdir(analysis_dir)

    dirs = sorted(get_dirs_in_path(result_path))

    collision_maps = []
    max = -1

    for dir in dirs:
        with open(os.path.join(dir, 'params.txt'), 'r') as file:
            params_s = file.read().replace('\n', '')
        params = ast.literal_eval(params_s)

        if params['env2'] is None:
            grid = CoopaModel(False, params['env_name']).grid
        else:
            grid = CoopaModel(False, params['env2']).grid

        collision_map = np.rot90(gather_collisions(dir, grid.width, grid.height))
        if np.max(collision_map) > max:
            max = np.max(collision_map)

        mask = np.zeros((grid.width, grid.height))
        for x, y in [(x, y) for x in range(grid.width) for y in range(grid.height)]:
            if type(grid.grid[x][y]) in [Shelf]:
                mask[x][y] = 1
        mask = np.rot90(mask)

        collision_maps.append((collision_map, mask, os.path.basename(dir)))

    for coll_map, mask, name in collision_maps:
        hmap = sns.heatmap(coll_map, yticklabels=False, xticklabels=False, square=True, cmap='Blues', mask=mask,
                           linewidths=0.1, vmax=max)
        hmap.set_facecolor('Brown')
        fig = hmap.get_figure()

        fig.savefig(os.path.join(analysis_dir, '{}.pdf'.format(name)), bbox_inches='tight')
        plt.close()