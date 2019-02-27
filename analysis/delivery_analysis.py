from utils import get_dirs_in_path
import ast
import os
import matplotlib.pyplot as plt
import shutil
import pickle

def get_buckets(stats, steps, bucket_size):
    buckets = [0 for _ in range(int(steps / bucket_size))]
    for run in stats.values():
        for agent in run.values():
            for delivery_time in agent['delivery_times']:
                bucket = int(delivery_time[1] / bucket_size)
                buckets[bucket] += 1
    buckets = [bucket / len(stats.values()) for bucket in buckets]
    return buckets

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
            if fname.isdigit():
                pkl = pickle.load(open(pkl_file, 'rb'))
                pkl['memories'] = pkl['memories'][-1]
                pkl['discriminators'] = pkl['discriminators'][-1]
                stats[run_id][fname] = pkl
    return stats

if __name__ == '__main__':
    result_path = r'/home/ottohant/language_experiments/results/stuff'
    analysis_dir = 'delivery_analysis'

    shutil.rmtree(analysis_dir, ignore_errors=True)
    print('')
    os.mkdir(analysis_dir)

    dirs = sorted(get_dirs_in_path(result_path))

    for dir in dirs:
        with open(os.path.join(dir, 'params.txt'), 'r') as file:
            params_s = file.read().replace('\n', '')
        param_dict = ast.literal_eval(params_s)
        # assert param_dict['env2'] is not None, "Run doesn't have second environment."
        agent_amount = param_dict['agents']
        if param_dict['env2'] is None:
            training_steps = 0
            steps = param_dict['steps']
        else:
            training_steps = param_dict['steps']
            steps = param_dict['env2_steps']
        lang_stats = get_stats(dir)

        bucket_size = 1000
        buckets = get_buckets(lang_stats, steps, bucket_size)
        x = [bucket_size * i for i in range(1, len(buckets) + 1)]

        plt.plot(x, buckets, label=training_steps)

    plt.xlabel('Time step')
    plt.ylabel('Deliveries made.')
    plt.legend()
    plt.show()
    # plt.savefig(os.path.join(analysis_dir, '{}.pdf'.format('deliveries_made')))
    # plt.close()