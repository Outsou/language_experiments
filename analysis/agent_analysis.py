import os
import pickle
import matplotlib.pyplot as plt
import shutil
from utils import get_dirs_in_path, mean_confidence_interval
from disc_tree import Categoriser
import ast
from analysis.query_game_analysis import get_success_buckets


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

def create_delivery_time_plots2(lang_stats, no_lang_stats, analysis_dir):
    '''Creates a delivery time plot. X-axis is delivery.'''
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

def get_tree_size(tree):
    nodes = [tree.root]
    size = 0
    while len(nodes) > 0:
        size += len(nodes)
        new_nodes = []
        for node in nodes:
            if node.child1 is not None:
                new_nodes.append(node.child1)
            if node.child2 is not None:
                new_nodes.append(node.child2)
        nodes = new_nodes
    return size

def get_buckets(stats, steps, bucket_size):
    buckets = [[] for _ in range(int(steps / bucket_size))]
    for run in stats.values():
        for agent in run.values():
            for delivery_time in agent['delivery_times']:
                bucket = int(delivery_time[1] / bucket_size)
                buckets[bucket].append(delivery_time[0])
    return [sum(bucket) / len(bucket) for bucket in buckets]

def create_delivery_time_plots(lang_stats, no_lang_stats, analysis_dir, steps, bucket_size, language_dir):
    '''Creates a delivery time plot. X-axis is time step.'''
    lang_buckets = [[] for _ in range(int(steps/bucket_size))]

    print('Loading query stats...')
    perfect_queries, one_right_queries, x = get_success_buckets(language_dir, steps, bucket_size)
    print('Done...\n')


    lang_buckets = get_buckets(lang_stats, steps, bucket_size)
    no_lang_buckets = get_buckets(no_lang_stats, steps, bucket_size)

    fig, ax1 = plt.subplots()
    lns1 = ax1.plot(x, lang_buckets, 'r-.', label='With language')
    lns2 = ax1.plot(x, no_lang_buckets, 'r:', label='Without language')
    ax1.set_xlabel('Time step')
    # plt.legend()
    # Make the y-axis label, ticks and tick labels match the line color.
    ax1.set_ylabel('Delivery time', color='r')
    ax1.tick_params('y', colors='r')
    ax2 = ax1.twinx()
    lns3 = ax2.plot(x, perfect_queries, 'b-', label='Perfect success')
    lns4 = ax2.plot(x, one_right_queries, 'b--', label='Partial success')
    ax2.set_ylabel('Success ratio', color='b')
    ax2.tick_params('y', colors='b')

    lns = lns1 + lns2 + lns3 + lns4
    labs = [l.get_label() for l in lns]
    ax1.legend(lns, labs)

    plt.savefig(os.path.join(analysis_dir, 'times_and_game_success.pdf'))
    plt.close()

def get_tree_size(tree):
    nodes = [tree.root]
    size = 0
    while len(nodes) > 0:
        size += len(nodes)
        new_nodes = []
        for node in nodes:
            if node.child1 is not None:
                new_nodes.append(node.child1)
            if node.child2 is not None:
                new_nodes.append(node.child2)
        nodes = new_nodes
    return size


def create_first_option_selected_plot(stats, analysis_dir, steps, bucket_size=500):
    buckets = [[] for _ in range(int(steps/bucket_size))]
    for run_stats in stats.values():
        for agent_stats in run_stats.values():
            for selected_option in agent_stats['selected_options']:
                bucket_idx = int(selected_option[1] / bucket_size)
                if selected_option[0] == 1:
                    buckets[bucket_idx].append(1)
                else:
                    buckets[bucket_idx].append(0)
    bucket_avgs = [sum(bucket) / len(bucket) for bucket in buckets]
    x = [bucket_size * i for i in range(1, len(buckets) + 1)]
    plt.plot(x, bucket_avgs)
    plt.xlabel('Time step')
    plt.ylabel('Option 1 selected ratio')
    plt.savefig(os.path.join(analysis_dir, 'option1_selected.pdf'))
    plt.close()

def analyse_disc_trees(lang_stats, analysis_dir):
    ranges = [(0, 0.5), (0.5, 1),
              (0, 0.25), (0.25, 0.5), (0.5, 0.75), (0.75, 1)]
              # (0, 0.125), (0.125, 0.25), (0.25, 0.375), (0.375, 0.5)]

    most_commons = {0: {}, 1: {}}
    for range in ranges:
        for channel in most_commons.keys():
            most_commons[channel][range] = []

    channel_sizes = {}
    # most_commons = {}
    for run_stats in lang_stats.values():
        words_used = {}
        for agent_stats in run_stats.values():
            for tree in agent_stats['discriminators'][0].trees:
                # Calculate tree size
                channel = tree.root.channel
                if channel not in channel_sizes:
                    channel_sizes[channel] = []
                channel_sizes[channel].append(get_tree_size(tree))

                # Calculate words used for every range
                if channel not in words_used:
                    words_used[channel] = {}
                    for range in ranges:
                        words_used[channel][range] = {}
                for range in ranges:
                    categoriser = Categoriser(range, channel)
                    word = agent_stats['memories'][0].get_form(categoriser)
                    if word is not None:
                        if word not in words_used[channel][range]:
                            words_used[channel][range][word] = 0
                        words_used[channel][range][word] += 1

        for channel, ranges in most_commons.items():
            for range in ranges:
                if len(words_used[channel][range].keys()) > 0:
                    most_common = max(words_used[channel][range].values())
                else:
                    most_common = 0
                most_commons[channel][range].append(most_common)

    for channel, ranges in most_commons.items():
        print('Channel {}'.format(channel))
        for range, counts in ranges.items():
            mean, interval = mean_confidence_interval(counts)
            print('{}: {}, +-{}'.format(range, mean, interval))
        print()

    for channel, sizes in channel_sizes.items():
        avg_size = sum(sizes) / len(sizes)
        print('Channel {} avg size: {}'.format(channel, avg_size))
        print('Channel {} min size: {}'.format(channel, min(sizes)))

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

if __name__ == '__main__':
    # result_dir_lang = r'/home/ottohant/Desktop/results_17-12-18_09-15-42'
    # result_dir_no_lang = r'/home/ottohant/Desktop/results_17-12-18_09-15-34'
    # result_dir_lang = r'/home/ottohant/Desktop/language_experiments/results_14-01-19_20-07-50_lang'
    result_dir_lang = r'/home/ottohant/language_experiments/results_16-01-19_12-33-26'
    result_dir_no_lang = r'/home/ottohant/language_experiments/results_16-01-19_10-14-02_shortest_no_lang'
    analysis_dir = 'agent_analysis'

    with open(os.path.join(result_dir_lang, 'params.txt'), 'r') as file:
        params_s = file.read().replace('\n', '')
    param_dict_lang = ast.literal_eval(params_s)

    print('Loading language stats...')
    lang_stats = get_stats(result_dir_lang)
    print('Done loading...')

    shutil.rmtree(analysis_dir, ignore_errors=True)
    print('')
    os.mkdir(analysis_dir)

    create_first_option_selected_plot(lang_stats, analysis_dir, param_dict_lang['steps'])

    # analyse_disc_trees(lang_stats, analysis_dir)
    #
    # print('Loading no language stats...')
    # no_lang_stats = get_stats(result_dir_no_lang)
    # print('Done loading...')
    #
    # print('Creating delivery time plots...')
    # # create_delivery_time_plots2(lang_stats, no_lang_stats, analysis_dir)
    # create_delivery_time_plots(lang_stats, no_lang_stats, analysis_dir, param_dict_lang['steps'], 500, result_dir_lang)
    #
    # print('Done...')
