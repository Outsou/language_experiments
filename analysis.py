import os
import pickle

def get_dirs_in_path(path):
    dirs = [os.path.join(path, file) for file in os.listdir(path) if os.path.isdir(os.path.join(path, file))]
    return dirs

def get_pickles_in_path(path):
    pickles = [os.path.join(path, file) for file in os.listdir(path) if file[-2:] == '.p']
    return pickles

if __name__ == '__main__':
    result_dir = '/home/ottohant/language_experiments/results_13-12-18_15-24-53'
    run_dirs = sorted(get_dirs_in_path(result_dir))
    run_pickles = []
    for run_dir in run_dirs:
        pickles = get_pickles_in_path(run_dir)
        run_pickles.append([])
        for pkl in pickles:
            run_pickles[-1].append(pickle.load(open(pkl, 'rb')))
    pass
    