from coopa_model import CoopaModel
from utils import get_neighborhood_str, create_heatmap, create_graphs
import time
import os
import numpy as np
from disc_tree import Categoriser
import matplotlib.pyplot as plt
import pickle


def run_experiment(run_id, directory, play_guessing, premade_lang, gather_stats):
    run_dir = os.path.join(directory, str(run_id))
    os.makedirs(run_dir)
    print('Running experiment...')
    model = CoopaModel(play_guessing, premade_lang, gather_stats)
    times = []
    start_time = time.time()
    period_start = time.time()
    timing_steps = 10000
    steps = 2000
    for i in range(1, steps + 1):
        if i % timing_steps == 0:
            times.append(time.time() - period_start)
            period_start = time.time()
            print('Time left: {}'.format(sum(times) / len(times) * ((steps - i) / timing_steps)))
        model.step()
    print()
    result_str = ''
    for agent in model.agents:
        result_str += '***************** AGENT {} *****************\n\n'.format(agent.color)
        for meaning, form in agent.memory.mf_dict.items():
            if type(meaning) is tuple:
                result_str += get_neighborhood_str(meaning)
                result_str += str(form) + '\n'
                result_str += str(agent.memory.meaning_stats[meaning]) + '\n\n'
            elif type(meaning) is Categoriser:
                result_str += 'Chan {}, range {}'.format(meaning.channel, meaning.range)
                result_str += str(form) + '\n'
                result_str += str(agent.memory.meaning_stats[meaning]) + '\n\n'
        result_str += str(np.rot90(agent.stat_dict['collision_map'])) + '\n\n'

    collisions = 0
    items_delivered = 0
    guessing_played = 0
    extra_distance = 0
    option1_selected = 0
    option2_selected = 0
    collision_map = np.zeros((model.grid.width, model.grid.height))
    delivery_times = []
    for agent in model.agents:
        collisions += agent.stat_dict['obs_game_init']
        items_delivered += agent.stat_dict['items_delivered']
        guessing_played += agent.stat_dict['guessing_game_init']
        option1_selected += agent.stat_dict['option1_selected']
        option2_selected += agent.stat_dict['option2_selected']
        extra_distance += agent.stat_dict['extra_distance']
        collision_map += agent.stat_dict['collision_map']
        disc_trees = create_graphs(agent.stat_dict['discriminators'][-1][0], agent.stat_dict['memories'][-1][0])
        for j in range(len(disc_trees)):
            chan = 'x' if j == 0 else 'y'
            disc_trees[j].render(filename='run{}_{}_{}'.format(run_id, agent.color, chan),
                                 directory=run_dir, cleanup=True)
        for j in range(len(agent.stat_dict['delivery_times'])):
            if j == len(delivery_times):
                delivery_times.append([])
            delivery_times[j].append(agent.stat_dict['delivery_times'][j])
        pickle.dump(agent.stat_dict, open(os.path.join(run_dir, '{}.p'.format(agent.color)), 'wb'))
        # asd = pickle.load(open(os.path.join(run_dir, '{}.p'.format(agent.color)), 'rb'))

    result_str += 'Collisions: {}\n'.format(collisions)
    result_str += 'Items delivered: {}\n'.format(items_delivered)
    result_str += 'Guessing played: {}\n'.format(guessing_played)
    result_str += 'Option 1 selected: {}\n'.format(option1_selected)
    result_str += 'Option 2 selected: {}\n'.format(option2_selected)
    result_str += 'Extra distance: {}\n'.format(extra_distance)

    with open(os.path.join(run_dir, 'run{}.txt'.format(run_id)), 'w') as text_file:
        print(result_str, file=text_file)

    print(result_str)
    print('Simulation took: {}'.format(time.time() - start_time))
    print()
    return items_delivered, collisions, collision_map, delivery_times

def get_avg_times(delivery_times):
    min_deliveries = min([len(x) for x in delivery_times])
    avg_times = []
    for j in range(min_deliveries):
        times = []
        for run_times in delivery_times:
            times += run_times[j]
        avg_times.append(sum(times) / len(times))
    return avg_times


if __name__ == "__main__":
    np.set_printoptions(suppress=True)
    items_delivered = []
    collisions = []
    collision_maps = []
    times = []
    runs = 5
    play_guessing = False
    premade_lang = False
    gather_stats = True
    date_time = time.strftime("%d-%m-%y_%H-%M-%S")
    directory = 'results_{}'.format(date_time)
    delivery_times = []
    for i in range(1, runs + 1):
        start_time = time.time()
        print('Starting run {}'.format(i))
        run_delivered, run_collisions, run_collision_map, run_delivery_times = run_experiment(i,
                                                                                              directory,
                                                                                              play_guessing,
                                                                                              premade_lang,
                                                                                              gather_stats)
        delivery_times.append(run_delivery_times)
        items_delivered.append(run_delivered)
        collisions.append(run_collisions)
        collision_maps.append(run_collision_map)
        times.append(time.time() - start_time)
        print('Finished run, time left {}'.format(sum(times) / len(times) * (runs - i)))
        print()

    avg_times = get_avg_times(delivery_times)
    plt.plot(avg_times)
    plt.savefig(os.path.join(directory, 'times.pdf'))
    plt.close()
    model = CoopaModel(False)
    collision_map = np.rot90(sum(collision_maps)) / runs
    create_heatmap(collision_map, model.grid, os.path.join(directory, 'collision_map.pdf'))
    create_heatmap(collision_map, model.grid, os.path.join(directory, 'collision_map.png'))

    with open(os.path.join(directory, 'final.txt'), 'w') as text_file:
        print('Delivered: {}, avg: {}'.format(items_delivered, np.mean(items_delivered)), file=text_file)
        print('Collisions: {}, avg: {}\n'.format(collisions, np.mean(collisions)), file=text_file)
        print(collision_map)
    # print(resources_delivered)
    # print(collisions)

    print('{}, finished'.format(directory))