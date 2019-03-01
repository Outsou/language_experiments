import shutil
import os
import pickle
import matplotlib.pyplot as plt
from utils import get_dirs_in_path
import numpy as np


def get_stats(result_path):
    '''Loads pickles in result path to a dictionary.'''
    run_dirs = sorted(get_dirs_in_path(result_path))
    stats = {}
    for run_dir in run_dirs:
        run_id = int(os.path.basename(run_dir))
        # print(run_id)
        pkl_file = os.path.join(run_dir, 'query_games.p')
        pkl = pickle.load(open(pkl_file, 'rb'))
        stats[run_id] = pkl
    return stats

def get_success_buckets(result_dir, steps, bucket_size):
    '''Returns ratios of partial and perfect success buckezied'''
    run_dirs = sorted(get_dirs_in_path(result_dir))
    perfect_buckets = [[] for _ in range(int(steps / bucket_size))]
    one_right_buckets = [[] for _ in range(int(steps / bucket_size))]
    for run_dir in run_dirs:
        pkl_file = os.path.join(run_dir, 'query_games.p')
        pkl = pickle.load(open(pkl_file, 'rb'))
        hearers = len(list(pkl[0]['answers']))
        for game in pkl:
            bucket_idx = int(game['time'] / bucket_size)
            speaker_categoriser = game['categoriser']
            speaker_place = game['place']
            categ_correct_count = 0
            place_correct_count = 0
            one_right = False
            for answer in game['answers'].values():
                if answer['categoriser'] == speaker_categoriser:
                    categ_correct_count += 1
                if answer['place'] == speaker_place:
                    place_correct_count += 1
                if answer['place'] == speaker_place and answer['categoriser'] == speaker_categoriser:
                    one_right = True
            if categ_correct_count == hearers and place_correct_count == hearers:
                perfect_buckets[bucket_idx].append(1)
            else:
                perfect_buckets[bucket_idx].append(0)
            if one_right:
                one_right_buckets[bucket_idx].append(1)
            else:
                one_right_buckets[bucket_idx].append(0)

    perfect_ratios = []
    for bucket_vals in perfect_buckets:
        if len(bucket_vals) > 0:
            perfect_ratios.append(sum(bucket_vals) / len(bucket_vals))
        else:
            perfect_ratios.append(0)
    # perfect_ratios = [sum(bucket_vals) / len(bucket_vals) for bucket_vals in perfect_buckets]
    x = [bucket_size * i for i in range(1, len(perfect_ratios) + 1)]

    one_right_ratios = []
    for bucket_vals in one_right_buckets:
        if len(bucket_vals) > 0:
            one_right_ratios.append(sum(bucket_vals) / len(bucket_vals))
        else:
            one_right_ratios.append(0)
    # one_right_ratios = [sum(bucket_vals) / len(bucket_vals) for bucket_vals in one_right_buckets]
    return perfect_ratios, one_right_ratios, x

def get_min_games(result_dir):
    run_dirs = sorted(get_dirs_in_path(result_dir))
    min = np.inf
    for run_dir in run_dirs:
        pkl_file = os.path.join(run_dir, 'query_games.p')
        pkl = pickle.load(open(pkl_file, 'rb'))
        if len(pkl) < min:
            min = len(pkl)
    return min

def create_success_plot(result_dir, analysis_dir, bucket_size=100):
    '''Creates of success rate for partial and perfect success. Also creates a plot that shows
    the portion of agents that made correct interpretations.'''
    run_dirs = sorted(get_dirs_in_path(result_dir))
    min_games = get_min_games(result_dir)
    correct_interpretations = [[] for _ in range(min_games)]
    all_correct = [[] for _ in range(min_games)]
    partial_correct = [[] for _ in range(min_games)]
    run_num = 0
    for run_dir in run_dirs:
        run_num += 1
        print('Run {}/{}'.format(run_num, len(run_dirs)))
        pkl_file = os.path.join(run_dir, 'query_games.p')
        run = pickle.load(open(pkl_file, 'rb'))
        hearers = len(list(run[0]['answers']))
        for i in range(min_games):
            speaker_categoriser = run[i]['categoriser']
            speaker_place = run[i]['place']
            categ_correct_count = 0
            place_correct_count = 0
            at_least_one = False
            for answer in run[i]['answers'].values():
                if answer['categoriser'] == speaker_categoriser:
                    categ_correct_count += 1
                if answer['place'] == speaker_place:
                    place_correct_count += 1
                if answer['place'] == speaker_place and answer['categoriser'] == speaker_categoriser:
                    at_least_one = True
            correct_interpretations[i].append(categ_correct_count)
            if categ_correct_count == hearers and place_correct_count == hearers:
                all_correct[i].append(1)
            else:
                all_correct[i].append(0)
            if at_least_one:
                partial_correct[i].append(1)
            else:
                partial_correct[i].append(0)

    correct_rate = [sum(interps) / len(interps) / hearers for interps in correct_interpretations]
    plt.plot(correct_rate)
    plt.ylabel('Correct interpretation rate')
    plt.xlabel('Game')
    plt.savefig(os.path.join(analysis_dir, '{}.pdf'.format('correct_interpretation_rate')))
    # plt.savefig(os.path.join(analysis_dir, '{}.png'.format(name)))
    plt.close()

    perfect_ratio = [sum(all_corr) / len(all_corr) for all_corr in all_correct]
    perfect_ratio = perfect_ratio[:-(len(perfect_ratio) % bucket_size)]
    perfect_ratio_windowed = [perfect_ratio[i:i + bucket_size] for i in range(0, len(perfect_ratio), bucket_size)]
    perfect_ratio_windowed = [sum(ratios) / len(ratios) for ratios in perfect_ratio_windowed]

    partial_ratio = [sum(partial_corr) / len(partial_corr) for partial_corr in partial_correct]
    partial_ratio = partial_ratio[:-(len(partial_ratio) % bucket_size)]
    partial_ratio_windowed = [partial_ratio[i:i + bucket_size] for i in range(0, len(partial_ratio), bucket_size)]
    partial_ratio_windowed = [sum(ratios) / len(ratios) for ratios in partial_ratio_windowed]

    x = [bucket_size * i for i in range(1, len(perfect_ratio_windowed) + 1)]
    plt.plot(x, perfect_ratio_windowed, 'b-', label='Perfect')
    plt.plot(x, partial_ratio_windowed, 'b--', label='Partial')
    plt.legend()
    plt.ylabel('Success ratio')
    plt.xlabel('Game')
    plt.savefig(os.path.join(analysis_dir, '{}.pdf'.format('query_success_ratio')))
    plt.close()

def analyse_synonymy(result_dir):
    run_dirs = sorted(get_dirs_in_path(result_dir))
    correct_count = 0
    synonymy_count = 0

    run = 0
    for run_dir in run_dirs:
        run += 1
        print('Analysing run {}/{}'.format(run, len(run_dirs)))
        pkl_file = os.path.join(run_dir, 'query_games.p')
        pkl = pickle.load(open(pkl_file, 'rb'))
        for game in pkl:
            for answer in game['answers'].values():
                if answer['categoriser'] == game['categoriser']:
                    correct_count += 1
                    if answer['categoriser_form'] != game['disc_form']:
                        synonymy_count += 1
    print('Synonymy: {}'.format(synonymy_count / correct_count))

def get_pickles_in_path(path):
    '''Returns the pickle filepaths in path.'''
    pickles = [os.path.join(path, file) for file in os.listdir(path) if file[-2:] == '.p' and file[:10] != 'place_game']
    return pickles

if __name__ == '__main__':
    result_dir = r'D:\resultit\beer_only2\results_26-02-19_23-21-35_random_lang'
    analysis_dir = 'query_game_analysis'

    shutil.rmtree(analysis_dir, ignore_errors=True)
    print('')
    os.mkdir(analysis_dir)

    # print('Loading query game stats...')
    # stats_dict = get_stats(result_dir)

    # print('Analysing synonymy...')
    # analyse_synonymy(result_dir)
    # print('Done.')

    print('Creating plots...')
    create_success_plot(result_dir, analysis_dir)
