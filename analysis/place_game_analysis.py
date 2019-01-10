import shutil
import os
import pickle
import matplotlib.pyplot as plt
from utils import get_neighborhood_str, get_dirs_in_path


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

def create_success_plot(sym_games, asym_games, analysis_dir, name='place_game_success'):
    def get_success_portion(games):
        success_count = [0] * len(games[0])
        for run_games in games:
            for i in range(len(run_games)):
                if run_games[i]['speaker_meaning'] == run_games[i]['hearer_interpretation']:
                    success_count[i] += 1
        return [x / len(games) for x in success_count]

    plt.plot(get_success_portion(sym_games), label='Symmetric')
    plt.plot(get_success_portion(asym_games), label='All', linestyle='dashed')
    plt.legend()
    plt.ylabel('Success rate')
    plt.xlabel('Game')
    plt.savefig(os.path.join(analysis_dir, '{}.pdf'.format(name)))
    plt.savefig(os.path.join(analysis_dir, '{}.png'.format(name)))
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
    pickles = [os.path.join(path, file) for file in os.listdir(path) if file[-2:] == '.p' and file[:10] != 'place_game']
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

def calculate_lexicon_cohesion(lexicons):
    union_size = 0
    intersect_size = 0
    same_count = 0
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

    print('Proportion of meanings shared by all agents: {}'.format(intersect_size / union_size))
    print('Proportion of shared meanings with same word: {}'.format(same_count / intersect_size))

    # Calculate shared meanings
    # Calculate word associated with them

def print_utilities(lexicons):
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

if __name__ == '__main__':
    # result_dir = '/home/ottohant/language_experiments/results_08-01-19_15-41-53'
    result_dir = r'C:\Users\otto\Desktop\results_08-01-19_15-41-53'
    analysis_dir = 'place_game_analysis'

    shutil.rmtree(analysis_dir, ignore_errors=True)
    print('')
    os.mkdir(analysis_dir)

    print('Loading place game stats...')
    stats_dict = get_stats(result_dir)

    # Trim stats
    # games, asym_games = trim_games(stats_dict)

    # create_success_plot(games, asym_games, analysis_dir)
    # create_success_plot(asym_games, analysis_dir, 'success_rate_asym')
    # create_success_plot2(games, analysis_dir)

    print('Loading lexicons...')
    lexicons = get_lexicons(result_dir)
    # calculate_lexicon_cohesion(lexicons)
    print()
    print_utilities(lexicons)

