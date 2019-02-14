import os
import pickle
import shutil
import ast
from utils import get_neighborhood_str

def get_dirs_in_path(path):
    '''Returns directories in path.'''
    dirs = [os.path.join(path, file) for file in os.listdir(path) if os.path.isdir(os.path.join(path, file))]
    return dirs

def get_pickles_in_path(path):
    '''Returns the pickle filepaths in path.'''
    pickles = [os.path.join(path, file) for file in os.listdir(path) if file[-2:] == '.p']
    return pickles

def get_stats(result_path):
    '''Loads pickles in result path to a dictionary.'''
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
                pkl['memories'] = pkl['memories'][-1]
                pkl['discriminators'] = pkl['discriminators'][-1]
                stats[run_id][fname] = pkl
    return stats

def analyse_route_concepts(stats):
    concepts = {}
    times = {}
    total = 0
    for run_stats in stats.values():
        for agent_stats in run_stats.values():
            for route_concept in agent_stats['route_concepts']:
                meaning1 = route_concept['option1']['meaning']
                if meaning1 is not None:
                    total += 1
                    if meaning1 not in concepts:
                        concepts[meaning1] = 0
                        times[meaning1] = []
                    concepts[meaning1] += 1
                    times[meaning1].append(route_concept['time'])
                meaning2 = route_concept['option2']['meaning']
                if meaning2 is not None:
                    total += 1
                    if meaning2 not in concepts:
                        concepts[meaning2] = 0
                        times[meaning2] = []
                    concepts[meaning2] += 1
                    times[meaning2].append(route_concept['time'])
    sorted_concepts = sorted(concepts.items(), key=lambda item: item[1], reverse=True)
    for concept in sorted_concepts:
        print(get_neighborhood_str(concept[0]))
        print(concept[1] / total * 100)
        print(sum(times[concept[0]]) / len(times[concept[0]]))
        print()

if __name__ == '__main__':
    result_dir = r'D:\resultit2\beer_only\results_14-02-19_09-48-41_random_lang'
    analysis_dir = 'conceptualization_analysis'

    with open(os.path.join(result_dir, 'params.txt'), 'r') as file:
        params_s = file.read().replace('\n', '')
    param_dict_lang = ast.literal_eval(params_s)

    shutil.rmtree(analysis_dir, ignore_errors=True)
    print('')
    os.mkdir(analysis_dir)

    print('Loading stats...')
    stats = get_stats(result_dir)
    print('Done loading.')

    analyse_route_concepts(stats)