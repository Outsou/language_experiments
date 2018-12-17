import os
import pickle
import matplotlib.pyplot as plt
import shutil
import time

def create_delivery_time_plots(stats):
    delivery_times = []
    for run_stats in stats.values():
        for agent_stats in run_stats.values():
            for i in range(len(agent_stats['delivery_times'])):
                if i == len(delivery_times):
                    delivery_times.append([])
                delivery_times[i].append(agent_stats['delivery_times'][i])
    max_len = len(delivery_times[0])
    i = 0
    length = len(delivery_times[i])
    while length == max_len:
        i += 1
        length = len(delivery_times[i])
    delivery_times = delivery_times[:i]
    avg_times = []
    for times in delivery_times:
        avg_times.append(sum(times) / len(times))
    plt.plot(avg_times)
    plt.savefig(os.path.join('anal_results', 'times.pdf'))
    plt.close()
    return delivery_times

def get_dirs_in_path(path):
    dirs = [os.path.join(path, file) for file in os.listdir(path) if os.path.isdir(os.path.join(path, file))]
    return dirs

def get_pickles_in_path(path):
    pickles = [os.path.join(path, file) for file in os.listdir(path) if file[-2:] == '.p']
    return pickles

if __name__ == '__main__':
    result_dir = r'C:\Users\otto\Documents\GitHub\language_experiments\results_17-12-18_09-15-42'
    run_dirs = sorted(get_dirs_in_path(result_dir))
    stats = {}
    shutil.rmtree('anal_results', ignore_errors=True)
    print('')
    os.mkdir('anal_results')
    for run_dir in run_dirs:
        run_id = int(os.path.basename(run_dir))
        # print(run_id)
        stats[run_id] = {}
        pickles = get_pickles_in_path(run_dir)
        for pkl_file in pickles:
            color = os.path.splitext(os.path.basename(pkl_file))[0]
            pkl = pickle.load(open(pkl_file, 'rb'))
            pkl['memories'] = pkl['memories'][-1]
            pkl['discriminators'] = pkl['discriminators'][-1]
            stats[run_id][color] = pkl

    create_delivery_time_plots(stats)
    