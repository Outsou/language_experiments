import shutil
import os
from utils import get_dirs_in_path
import pickle
import matplotlib.pyplot as plt
from utils import mean_confidence_interval
import ast


def make_most_common_plot(step_words, agents, run_id):
    most_common = []
    for step_dict in step_words:
        amounts = step_dict.values()
        if len(amounts) == 0:
            most_common.append(0)
        else:
            most_common.append(max(amounts))

    last_idx = 0
    for i in range(len(most_common)):
        if most_common[i] < agents:
            last_idx = i + 100

    most_common = most_common[:last_idx]

    plt.plot(most_common)
    plt.xlabel('Time step')
    plt.ylabel('Agents')
    plt.savefig(os.path.join(analysis_dir, 'top_coherence_{}.pdf'.format(run_id)))
    plt.savefig(os.path.join(analysis_dir, 'top_coherence_{}.png'.format(run_id)))
    plt.close()

    return last_idx

def make_word_battle_plot(step_words, last_idx, run_id):
    words = set()
    for step_dict in step_words:
        for word in step_dict.keys():
            words.add(word)

    word_popularity = {}
    for word in words:
        word_popularity[word] = []
        for step_dict in step_words:
            if word not in step_dict:
                word_popularity[word].append(0)
            else:
                word_popularity[word].append(step_dict[word])

    for word in words:
        plt.plot(word_popularity[word][:last_idx], label=word)
    plt.legend()
    plt.xlabel('Time step')
    plt.ylabel('Agents')
    plt.savefig(os.path.join(analysis_dir, 'top_coherence_{}_battle.png'.format(run_id)))
    plt.close()

def analyse_run(run_dir, steps):
    # top_meaning = (('S', 'S', 'S'), ('.', 'X', '.'), ('S', 'S', 'S'))
    top_meaning = (('S', '.', 'S'), ('S', 'X', 'S'), ('S', '.', 'S'))
    # top_meaning = (('.', '.', '.'), ('S', 'X', 'S'), ('S', '.', 'S'))
    deliveries = 0
    collisions = 0
    delivery_times = []

    pickles = [os.path.join(run_dir, file) for file in os.listdir(run_dir)
               if file[-2:] == '.p' and file[:5] != 'place' and file[:5] != 'query']
    agent_stats = []
    for pkl_file in pickles:
        agent_stats.append(pickle.load(open(pkl_file, 'rb')))

    step_words = [{} for _ in range(steps)]
    for stats in agent_stats:
        deliveries += stats['items_delivered']
        collisions += stats['obs_game_init']
        delivery_times += [x[0] for x in stats['delivery_times']]
        for i in range(len(stats['memories'])):
            start = stats['memories'][i][1]
            if i < len(stats['memories']) - 1:
                end = stats['memories'][i+1][1]
            else:
                end = len(step_words)
            form = stats['memories'][i][0].get_form(top_meaning)
            if form is not None:
                for j in range(start, end):
                    if form not in step_words[j]:
                        step_words[j][form] = 0
                    step_words[j][form] += 1

    run_id = os.path.basename(run_dir)
    last_idx = make_most_common_plot(step_words, len(agent_stats), run_id)
    # make_word_battle_plot(step_words, last_idx, run_id)

    return deliveries, collisions, len(agent_stats), delivery_times

if __name__ == '__main__':
    result_dir = r'D:\resultit\beer_only2\results_26-02-19_23-21-35_random_lang'
    analysis_dir = 'run_analysis'

    with open(os.path.join(result_dir, 'params.txt'), 'r') as file:
        params_s = file.read().replace('\n', '')
    param_dict = ast.literal_eval(params_s)

    shutil.rmtree(analysis_dir, ignore_errors=True)
    print('')
    os.mkdir(analysis_dir)

    run_dirs = sorted(get_dirs_in_path(result_dir))
    i = 0
    deliveries = []
    collisions = []
    delivery_times = []
    for run_dir in run_dirs:
        i += 1
        print('Analysing run {}/{}'.format(i, len(run_dirs)))
        run_deliveries, run_collisions, agents, run_times = analyse_run(run_dir, param_dict['steps'])
        deliveries.append(run_deliveries / agents)
        collisions.append(run_collisions / agents)
        delivery_times += run_times

    mean, h = mean_confidence_interval(deliveries)
    print('Deliveries mean: {} {}'.format(mean, h))
    mean, h = mean_confidence_interval(collisions)
    print('Collisions mean: {} {}'.format(mean, h))
    print('Delivery mean: {}'.format(sum(delivery_times) / len(delivery_times)))
