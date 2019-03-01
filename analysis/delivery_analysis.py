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
            for delivery_time in agent:
                bucket = int(delivery_time[1] / bucket_size)
                buckets[bucket] += 1
    buckets = [bucket / len(stats.values()) for bucket in buckets]
    return buckets

def get_pickles_in_path(path):
    '''Returns the pickle filepaths in path.'''
    pickles = [os.path.join(path, file) for file in os.listdir(path) if file[-2:] == '.p']
    return pickles

def get_delivery_stats(result_path):
    '''Loads pickles in result path to a dictionary.'''
    run_dirs = sorted(get_dirs_in_path(result_path))
    stats = {}
    count = 0
    print('loading runs...')
    for run_dir in run_dirs:
        count +=1
        # print('{}/{}'.format(count, len(run_dirs)))
        run_id = int(os.path.basename(run_dir))
        # print(run_id)
        stats[run_id] = {}
        pickles = get_pickles_in_path(run_dir)
        for pkl_file in pickles:
            fname = os.path.splitext(os.path.basename(pkl_file))[0]
            if fname.isdigit():
                pkl = pickle.load(open(pkl_file, 'rb'))
                stats[run_id][fname] = pkl['delivery_times']
    return stats

def create_delivery_plot(dirs, analysis_dir):
    for dir in dirs:
        with open(os.path.join(dir, 'params.txt'), 'r') as file:
            params_s = file.read().replace('\n', '')
        param_dict = ast.literal_eval(params_s)
        if param_dict['env2'] is None:
            training_steps = 0
            steps = param_dict['steps']
        else:
            training_steps = param_dict['steps']
            steps = param_dict['env2_steps']
        lang_stats = get_delivery_stats(dir)

        bucket_size = 1000
        buckets = get_buckets(lang_stats, steps, bucket_size)
        x = [bucket_size * i for i in range(1, len(buckets) + 1)]
        if 'premade_lang' in param_dict and param_dict['premade_lang']:
            label = 'Premade lang'
        else:
            label = training_steps
        plt.plot(x, buckets, label=label)
    plt.xlabel('Time step')
    plt.ylabel('Deliveries made.')
    plt.legend()
    plt.savefig(os.path.join(analysis_dir, '{}.pdf'.format('deliveries_made')))
    plt.close()

def create_query_game_success_plot(dirs, analysis_dir):
    line_types = ['solid', 'dashed', 'dashdot', 'dotted']
    line_type_idx = 0
    for dir in dirs:
        with open(os.path.join(dir, 'params.txt'), 'r') as file:
            params_s = file.read().replace('\n', '')
        param_dict = ast.literal_eval(params_s)
        if param_dict['env2'] is None:
            training_steps = 0
            steps = param_dict['steps']
        else:
            training_steps = param_dict['steps']
            steps = param_dict['env2_steps']

        run_dirs = sorted(get_dirs_in_path(dir))
        bucket_size = 1000
        correct_interpretations = [[] for _ in range(int(steps / bucket_size))]
        all_correct = [[] for _ in range(int(steps / bucket_size))]
        partial_correct = [[] for _ in range(int(steps / bucket_size))]
        run_num = 0
        total_incorrect = 0
        place_incorrect = 0
        disc_incorrect = 0
        both_incorrect = 0
        total = 0
        for run_dir in run_dirs:
            run_num += 1
            # print('Run {}/{}'.format(run_num, len(run_dirs)))
            pkl_file = os.path.join(run_dir, 'query_games.p')
            run = pickle.load(open(pkl_file, 'rb'))
            hearers = len(list(run[0]['answers']))
            for game in run:
                bucket = int(game['time'] / bucket_size)
                speaker_categoriser = game['categoriser']
                speaker_place = game['place']
                categ_correct_count = 0
                place_correct_count = 0
                at_least_one = False
                for answer in game['answers'].values():
                    if answer['categoriser'] == speaker_categoriser:
                        categ_correct_count += 1
                    if answer['place'] == speaker_place:
                        place_correct_count += 1
                    if answer['place'] == speaker_place and answer['categoriser'] == speaker_categoriser:
                        at_least_one = True
                correct_interpretations[bucket].append(categ_correct_count)

                # Perfect success
                if categ_correct_count == hearers and place_correct_count == hearers:
                    all_correct[bucket].append(1)
                else:
                    all_correct[bucket].append(0)
                    if categ_correct_count < hearers:
                        disc_incorrect += 1
                    if place_correct_count < hearers:
                        place_incorrect += 1
                    if place_correct_count < hearers and categ_correct_count < hearers:
                        both_incorrect += 1
                    total_incorrect += 1

                # Partial success
                if at_least_one:
                    partial_correct[bucket].append(1)
                else:
                    partial_correct[bucket].append(0)

                total += 1

        perfect_ratio = [sum(all_corr) / len(all_corr) for all_corr in all_correct]
        x = [bucket_size * i for i in range(1, len(perfect_ratio) + 1)]
        if 'premade_lang' in param_dict and param_dict['premade_lang']:
            label = 'Premade lang'
        else:
            label = training_steps
        plt.plot(x, perfect_ratio, ls=line_types[line_type_idx], label=label)
        line_type_idx += 1

        print(label)
        print('Incorrect: {}'.format(total_incorrect / total))
        print('Amount of gaems: {}'.format(total / len(run_dirs)))
        print('Both incorrect: {}'.format(both_incorrect / total_incorrect))
        print('Categoriser incorrect: {}'.format(disc_incorrect / total_incorrect))
        print('Place incorrect: {}'.format(place_incorrect / total_incorrect))
        print('')

    ax = plt.gca()
    handles, labels = ax.get_legend_handles_labels()
    labels, handles = zip(*sorted(zip(labels, handles), key=lambda t: t[0]))
    ax.legend(handles, labels)

    plt.ylabel('Success ratio')
    plt.xlabel('Time step')
    plt.savefig(os.path.join(analysis_dir, '{}.pdf'.format('query_success_ratio')))
    plt.close()

if __name__ == '__main__':
    result_path = r'/home/ottohant/language_experiments/results/vaihtis_small'
    analysis_dir = 'delivery_analysis'

    shutil.rmtree(analysis_dir, ignore_errors=True)
    print('')
    os.mkdir(analysis_dir)

    dirs = sorted(get_dirs_in_path(result_path))
    print('Calculating query game success stuff...')
    create_query_game_success_plot(dirs, analysis_dir)
    # print('Calculating delivery amount stuff...')
    # create_delivery_plot(dirs, analysis_dir)
