import shutil
import os
import pickle
import matplotlib.pyplot as plt
from utils import get_neighborhood_str, get_dirs_in_path
from disc_tree import Categoriser


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

def trim_games(stats_dict):
    '''Removes games where speaker and hearer don't have the same observation.
    Returns a list where all runs have the same amount of game rounds.'''
    games = stats_dict.values()
    trimmed_games = []
    total_count = 0
    trimmed_count = 0
    for run_games in games:
        trimmed = [x for x in run_games if x['speaker_meaning'] == x['hearer_meaning']]
        total_count += len(run_games)
        trimmed_count += len(trimmed)
        trimmed_games.append(trimmed)

    print('Trimmed proportion: {}'.format(trimmed_count / total_count))
    # trimmed_games = stats_dict.values()

    min_games = min([len(x) for x in trimmed_games])
    return [x[:min_games] for x in trimmed_games], [x[:min_games] for x in stats_dict.values()]

def create_success_plot(stat_dict, analysis_dir):
    min_games = min([len(games) for games in stat_dict.values()])
    correct_interpretations = [[] for _ in range(min_games)]
    all_correct = [[] for _ in range(min_games)]
    hearers = len(list(stats_dict.values())[0][0]['answers'])
    for run in stats_dict.values():
        for i in range(min_games):
            speaker_categoriser = run[i]['categoriser']
            speaker_place = run[i]['place']
            categ_correct_count = 0
            place_correct_count = 0
            for answer in run[i]['answers'].values():
                if answer['categoriser'] == speaker_categoriser:
                    categ_correct_count += 1
                if answer['place'] == speaker_place:
                    place_correct_count += 1
            correct_interpretations[i].append(categ_correct_count)
            if categ_correct_count == hearers and place_correct_count == hearers:
                all_correct[i].append(1)
            else:
                all_correct[i].append(0)

    correct_rate = [sum(interps) / len(interps) / hearers for interps in correct_interpretations]
    plt.plot(correct_rate)
    plt.ylabel('Correct interpretation rate')
    plt.xlabel('Game')
    plt.savefig(os.path.join(analysis_dir, '{}.pdf'.format('correct_interpretation_rate')))
    # plt.savefig(os.path.join(analysis_dir, '{}.png'.format(name)))
    plt.close()

    n = 100
    correct_ratio = [sum(all_corr) / len(all_corr) for all_corr in all_correct]
    correct_ratio = correct_ratio[:-(len(correct_ratio) % n)]
    windowed_ratio = [correct_ratio[i:i + n] for i in range(0, len(correct_ratio), n)]
    windowed_ratio = [sum(ratios) / len(ratios) for ratios in windowed_ratio]
    x = [n * i for i in range(1, len(windowed_ratio) + 1)]
    plt.plot(x, windowed_ratio)
    plt.ylabel('All interpretations correct ratio')
    plt.xlabel('Game')
    plt.savefig(os.path.join(analysis_dir, '{}.pdf'.format('all_correct_ratio')))
    plt.close()


def get_pickles_in_path(path):
    '''Returns the pickle filepaths in path.'''
    pickles = [os.path.join(path, file) for file in os.listdir(path) if file[-2:] == '.p' and file[:10] != 'place_game']
    return pickles

if __name__ == '__main__':
    result_dir = '/home/ottohant/language_experiments/results_11-01-19_14-45-23'
    analysis_dir = 'query_game_analysis'

    shutil.rmtree(analysis_dir, ignore_errors=True)
    print('')
    os.mkdir(analysis_dir)

    print('Loading query game stats...')
    stats_dict = get_stats(result_dir)

    # ranges = [(0, 0.5), (0.5, 1),
    #           (0, 0.25), (0.25, 0.5), (0.5, 0.75), (0.75, 1)]
    # channels = [0, 1]
    #
    # categorisers = []
    # for channel in channels:
    #     for rng in ranges:
    #         categorisers.append(Categoriser(rng, channel))

    create_success_plot(stats_dict, analysis_dir)

