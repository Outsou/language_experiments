import shutil
import os
import pickle
import matplotlib.pyplot as plt

def get_dirs_in_path(path):
    '''Returns directories in path.'''
    dirs = [os.path.join(path, file) for file in os.listdir(path) if os.path.isdir(os.path.join(path, file))]
    return dirs

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
    for run_games in games:
        trimmed_games.append([x for x in run_games if x['speaker_meaning'] == x['hearer_meaning']])

    min_games = min([len(x) for x in trimmed_games])
    return [x[:min_games] for x in trimmed_games]

def create_success_plot(games, analysis_dir):
    success_count = [0] * len(games[0])
    for run_games in games:
        for i in range(len(run_games)):
            if run_games[i]['speaker_meaning'] == run_games[i]['hearer_interpretation']:
                success_count[i] += 1
    success_portion = [x / len(games) for x in success_count]

    plt.plot(success_portion)
    plt.ylabel('Success rate')
    plt.xlabel('Game')
    plt.savefig(os.path.join(analysis_dir, 'success_rate.pdf'))
    plt.savefig(os.path.join(analysis_dir, 'success_rate.png'))
    plt.close()

if __name__ == '__main__':
    result_dir = '/home/ottohant/language_experiments/results_08-01-19_15-34-03'
    analysis_dir = 'place_game_analysis'

    shutil.rmtree(analysis_dir, ignore_errors=True)
    print('')
    os.mkdir(analysis_dir)

    print('Loading place game stats...')
    stats_dict = get_stats(result_dir)

    # Trim stats
    games = trim_games(stats_dict)

    create_success_plot(games, analysis_dir)
