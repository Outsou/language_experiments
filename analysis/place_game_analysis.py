import shutil
import os
import pickle
import matplotlib.pyplot as plt
from utils import get_neighborhood_str, get_dirs_in_path
import itertools
import ast


def get_stats(result_path):
    '''Loads pickles in result path to a dictionary.'''
    run_dirs = sorted(get_dirs_in_path(result_path))
    stats = {}
    for run_dir in run_dirs:
        run_id = int(os.path.basename(run_dir))
        # print(run_id)
        pkl_file = os.path.join(run_dir, 'place_games.p')
        pkl = pickle.load(open(pkl_file, 'rb'))
        stats[run_id] = pkl
    return stats

def trim_games(stats_dict):
    '''Returns a list of only symmetric games and a list of all games,'''
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

    # min_games = min([len(x) for x in trimmed_games])
    # return [x[:min_games] for x in trimmed_games], [x[:min_games] for x in stats_dict.values()]
    return trimmed_games, list(stats_dict.values())

def create_success_plot(sym_games, asym_games, analysis_dir, pkl_name, pkl_label, steps, bucket_size=500):
    '''Creates a plot where the success rate of the nth game is shown.'''
    def get_success_portion(games):
        success_buckets = [[] for _ in range(int(steps / bucket_size))]
        for run_games in games:
            for i in range(len(run_games)):
                bucket_idx = int(run_games[i]['time'] / bucket_size)
                if run_games[i]['speaker_meaning'] == run_games[i]['hearer_interpretation']:
                    success_buckets[bucket_idx].append(1)
                else:
                    success_buckets[bucket_idx].append(0)
        return [sum(x) / len(x) for x in success_buckets]

    sym_buckets = get_success_portion(sym_games)
    asym_buckets = get_success_portion(asym_games)
    x = [bucket_size * i for i in range(1, len(sym_buckets) + 1)]
    plt.plot(x, sym_buckets, label='Symmetric')
    plt.plot(x, asym_buckets, label='All', linestyle='dashed')
    plt.legend()
    plt.ylabel('Success rate')
    plt.xlabel('Game')
    plt.savefig(os.path.join(analysis_dir, 'place_game_success.pdf'))
    # plt.savefig(os.path.join(analysis_dir, 'place_game_success.png'))
    plt.close()

    pickle.dump({'buckets': sym_buckets, 'bucket_size': bucket_size, 'label': pkl_label}, open(pkl_name, 'wb'))

def create_success_plot_from_pkls(pkl_dir, analysis_dir):
    pkls = []
    pickles = get_pickles_in_path(pkl_dir)
    for pkl_file in pickles:
        pkl = pickle.load(open(pkl_file, 'rb'))
        pkls.append(pkl)
    lengths = [len(x['buckets']) for x in pkls]
    assert len(set(lengths)) == 1, 'Pkl files have different sized lists'
    bucket_sizes = [x['bucket_size'] for x in pkls]
    assert len(set(bucket_sizes)) == 1, 'Different bucket sizes'

    x = [bucket_sizes[0] * i for i in range(1, lengths[0] + 1)]
    for pkl in pkls:
        plt.plot(x, pkl['buckets'], label=pkl['label'])
    plt.legend()
    plt.savefig(os.path.join(analysis_dir, 'multi_setup_success.pdf'))
    plt.close()

# def create_success_plot2(games, analysis_dir):
#     highest_step = games[0][-1]['time']
#     for run_games in games:
#         last_step = run_games[-1]['time']
#         if last_step > highest_step:
#             highest_step = last_step
#     step_success = [[] for _ in range(highest_step + 1)]
#
#     for run_games in games:
#         for game in run_games:
#             if game['speaker_meaning'] == game['hearer_interpretation']:
#                 step_success[game['time']].append(1)
#             else:
#                 step_success[game['time']].append(0)
#
#     print('asd')
#
#     # plt.plot(success_portion)
#     # plt.ylabel('Success rate')
#     # plt.xlabel('Game')
#     # plt.savefig(os.path.join(analysis_dir, 'success_rate.pdf'))
#     # plt.savefig(os.path.join(analysis_dir, 'success_rate.png'))
#     # plt.close()

def get_pickles_in_path(path):
    '''Returns the pickle filepaths in path.'''
    if not os.path.isdir(path):
        print('No pickels in path!')
        return None
    pickles = [os.path.join(path, file) for file in os.listdir(path)
               if file[-2:] == '.p' and file[:5] != 'place' and file[:5] != 'query']
    return pickles

def get_lexicons(result_path):
    '''Loads pickles in result path to a dictionary.'''
    run_dirs = sorted(get_dirs_in_path(result_path))
    lexicons = []
    for run_dir in run_dirs:
        run_id = int(os.path.basename(run_dir))
        # print(run_id)
        lexicons.append([])
        pickles = get_pickles_in_path(run_dir)
        for pkl_file in pickles:
            pkl = pickle.load(open(pkl_file, 'rb'))
            lexicons[-1].append(pkl['memories'][-1][0])
    return lexicons

def calculate_lexicon_cohesion(lexicons, meanings=[]):
    '''Prints some stats about the cohesion of the agents' lexicons.'''
    union_size = 0
    intersect_size = 0
    same_count = 0
    meanings_same = [0 for _ in meanings]
    all_same = 0
    for run_lexicons in lexicons:
        meaning_sets = []
        for lexicon in run_lexicons:
            meaning_sets.append(set(lexicon.mf_dict.keys()))
        union = set.union(*meaning_sets)
        intersect = set.intersection(*meaning_sets)
        union_size += len(union)
        intersect_size += len(intersect)

        for meaning in intersect:
            forms = set([lexicon.get_form(meaning) for lexicon in run_lexicons])
            if len(forms) == 1:
                same_count += 1

        meaning_word_counts = []
        for i in range(len(meanings)):
            run_meanings = set()
            for lexicon in run_lexicons:
                run_meanings.add(lexicon.get_form(meanings[i]))
            if len(run_meanings) == 1:
                meanings_same[i] += 1
            meaning_word_counts.append(len(run_meanings))
        if all(map(lambda x: x == 1, meaning_word_counts)):
            all_same += 1

    print('Proportion of meanings shared by all agents: {}'.format(intersect_size / union_size))
    print('Proportion of shared meanings with same word: {}'.format(same_count / intersect_size))
    print()
    for i in range(len(meanings_same)):
        print('{}. same: {}'.format(i + 1, meanings_same[i] / len(lexicons)))
    print('All same: {}'.format(all_same / len(lexicons)))

def print_utilities(lexicons):
    '''Prints the place meanings and their utilities in sorted order.
    Returns two most important meanings.'''
    importances = {}
    for run_lexicons in lexicons:
        for lexicon in run_lexicons:
            meanings = lexicon.mf_dict.keys()
            for meaning in meanings:
                if meaning not in importances:
                    importances[meaning] = []
                utility = lexicon.get_utility(meaning)
                if utility is not None:
                    importances[meaning].append(utility)
    avg_utilities = {}
    for meaning in importances.keys():
        if len(importances[meaning]) > 0:
            avg_utilities[meaning] = sum(importances[meaning]) / len(importances[meaning])
    sorted_utilities = list(avg_utilities.items())
    sorted_utilities.sort(key=lambda tup: tup[1])
    for meaning, util in sorted_utilities:
        print(get_neighborhood_str(meaning))
        print(util)
        print()

    return [sorted_utilities[0][0], sorted_utilities[1][0]]

def collisions_plot(stats_dict, analysis_dir, steps, bucket_size=500):
    '''Creates a plot of collisions happening in the last bucket_size time steps.'''
    buckets = [0 for _ in range(int(steps / bucket_size))]
    for game in itertools.chain.from_iterable(stats_dict.values()):
        bucket_idx = int(game['time'] / bucket_size)
        buckets[bucket_idx] += 1

    x = [bucket_size * i for i in range(1, len(buckets) + 1)]
    plt.plot(x, buckets)
    plt.xlabel('Time step')
    plt.ylabel('Collisions')
    plt.savefig(os.path.join(analysis_dir, 'collisions.pdf'))
    plt.close()

if __name__ == '__main__':
    result_dir = '/home/ottohant/language_experiments/results_08-01-19_15-41-53'
    # result_dir = '/home/ottohant/Desktop/language_experiments/results_14-01-19_20-07-50_lang'
    # result_dir = r'C:\Users\otto\Desktop\results_08-01-19_15-41-53'
    analysis_dir = 'place_game_analysis'

    pkl_dir = 'pkls'
    if not os.path.isdir(pkl_dir):
        os.makedirs(pkl_dir)

    with open(os.path.join(result_dir, 'params.txt'), 'r') as file:
        params_s = file.read().replace('\n', '')
    param_dict = ast.literal_eval(params_s)

    shutil.rmtree(analysis_dir, ignore_errors=True)
    print('')
    os.mkdir(analysis_dir)

    print('Loading place game stats...')
    stats_dict = get_stats(result_dir)

    # Trim stats
    games, asym_games = trim_games(stats_dict)

    # collisions_plot(stats_dict, analysis_dir, param_dict['steps'])
    collisions_plot(stats_dict, analysis_dir, 20000)

    pkl_label = 'Query Game setup' if param_dict['play_guessing'] else 'Place Game setup'
    create_success_plot(games, asym_games, analysis_dir,
                        os.path.join(pkl_dir, os.path.basename(result_dir) + '.p'), pkl_label,
                        20000)

    create_success_plot_from_pkls(pkl_dir, analysis_dir)

    # create_success_plot(asym_games, analysis_dir, 'success_rate_asym')
    # create_success_plot2(games, analysis_dir)
    #
    # print('Loading lexicons...')
    # lexicons = get_lexicons(result_dir)
    # top2 = print_utilities(lexicons)
    # calculate_lexicon_cohesion(lexicons, top2)
    # print()


