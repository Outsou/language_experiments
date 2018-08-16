from coopa_model import CoopaModel
from utils import get_neighborhood_str
import time
import os
import numpy as np


def run_experiment(run_id, directory, play_guessing):
    print('Running experiment...')
    model = CoopaModel(play_guessing)
    times = []
    start_time = time.time()
    period_start = time.time()
    timing_steps = 10000
    steps = 50000
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
                result_str += get_neighborhood_str(meaning) + '\n'
                result_str += str(form) + '\n'
                result_str += str(agent.memory.meaning_stats[meaning]) + '\n\n'

    collisions = 0
    travel_distance = 0
    resources_delivered = 0
    for agent in model.agents:
        collisions += agent.stat_dict['obs_game_init']
        travel_distance += agent.stat_dict['travel_distance']
        resources_delivered += agent.stat_dict['resources_delivered']
        for j in range(len(agent.stat_dict['disc_trees'][-1])):
            chan = 'x' if j == 0 else 'y'
            agent.stat_dict['disc_trees'][-1][j].render(filename='run{}_{}_{}'.format(run_id, agent.color, chan),
                                                        directory=directory, cleanup=True)
    result_str += 'Collisions: {}\n'.format(collisions)
    result_str += 'Travel distance: {}\n'.format(travel_distance)
    result_str += 'Resources delivered: {}\n'.format(resources_delivered)

    with open(os.path.join(directory, 'run{}.txt'.format(run_id)), 'w') as text_file:
        print(result_str, file=text_file)

    print(result_str)
    print('Simulation took: {}'.format(time.time() - start_time))
    print()
    return resources_delivered, collisions

if __name__ == "__main__":
    resources_delivered = []
    collisions = []
    times = []
    runs = 30
    play_guessing = False
    date_time = time.strftime("%d-%m-%y_%H-%M-%S")
    directory = 'results_{}'.format(date_time)
    for i in range(1, runs + 1):
        start_time = time.time()
        print('Starting run {}'.format(i))
        run_delivered, run_collisions = run_experiment(i, directory, play_guessing)
        resources_delivered.append(run_delivered)
        collisions.append(run_collisions)
        times.append(time.time() - start_time)
        print('Finished run, time left {}'.format(sum(times) / len(times) * (runs - i)))
        print()

    with open(os.path.join(directory, 'final.txt'), 'w') as text_file:
        print('Delivered: {}, avg: {}'.format(resources_delivered, np.mean(resources_delivered)), file=text_file)
        print('Collsions: {}, avg: {}'.format(collisions, np.mean(collisions)), file=text_file)
    # print(resources_delivered)
    # print(collisions)
