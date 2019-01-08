import os
import pickle
import matplotlib.pyplot as plt
import shutil

def sliding_window(val_list, window_size=10):
    '''Returns a list containing sliding window sums on val_list.'''
    window_sums = []
    for i in range(window_size - 1, len(val_list)):
        window_sums.append(sum(val_list[i - window_size + 1:i + 1]))
    x = list(range(window_size, len(val_list) + 1))
    return window_sums, x

def get_avg_times(stats):
    '''Returns the average delivery times.'''
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
    return avg_times

def create_delivery_time_plots(lang_stats, no_lang_stats, analysis_dir):
    '''Creates a delivery time plot.'''
    avg_times_lang =  get_avg_times(lang_stats)[1:] # first element dropped
    avg_times_no_lang = get_avg_times(no_lang_stats)[1:]

    w_size = 10
    windowed_lang, x1 = sliding_window(avg_times_lang, window_size=w_size)
    windowed_no_lang, x2 = sliding_window(avg_times_no_lang, window_size=w_size)

    if len(windowed_lang) > len(windowed_no_lang):
        windowed_lang = windowed_lang[:len(windowed_no_lang)]
        x = x2
    else:
        windowed_no_lang = windowed_no_lang[:len(windowed_lang)]
        x = x1

    plt.plot(x[0::w_size], windowed_lang[0::w_size], label='Language')
    plt.plot(x[0::w_size], windowed_no_lang[0::w_size], label='No language', linestyle='dashed')
    plt.ylabel('Time steps used for last {} deliveries'.format(w_size))
    plt.xlabel('Delivery')
    plt.legend()
    plt.savefig(os.path.join(analysis_dir, 'times.pdf'))
    plt.savefig(os.path.join(analysis_dir, 'times.png'))
    plt.close()

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
            color = os.path.splitext(os.path.basename(pkl_file))[0]
            pkl = pickle.load(open(pkl_file, 'rb'))
            pkl['memories'] = pkl['memories'][-1]
            pkl['discriminators'] = pkl['discriminators'][-1]
            stats[run_id][color] = pkl
    return stats

if __name__ == '__main__':
    # result_dir_lang = r'/home/ottohant/Desktop/results_17-12-18_09-15-42'
    # result_dir_no_lang = r'/home/ottohant/Desktop/results_17-12-18_09-15-34'
    result_dir_lang = r'/home/ottohant/language_experiments/results_07-01-19_12-40-30_random_lang'
    result_dir_no_lang = r'/home/ottohant/language_experiments/results_07-01-19_10-20-15_random'
    analysis_dir = 'analysis_results'

    print('Loading language stats...')
    lang_stats = get_stats(result_dir_lang)
    print('Loading no language stats...')
    no_lang_stats = get_stats(result_dir_no_lang)

    shutil.rmtree(analysis_dir, ignore_errors=True)
    print('')
    os.mkdir(analysis_dir)

    print('Creating delivery time plots...')
    create_delivery_time_plots(lang_stats, no_lang_stats, analysis_dir)

    print('Done...')
