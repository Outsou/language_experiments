from coopa_model import CoopaModel
from utils import get_neighborhood_str, create_heatmap, create_graphs
import time
import datetime
import os
import numpy as np
from disc_tree import Categoriser
import pickle
import pprint


def run_experiment(run_id, directory, play_guessing, gather_stats, random_behaviour, steps, create_trees,
                   agents, env_name, route_conceptualization):
    run_dir = os.path.join(directory, str(run_id))
    os.makedirs(run_dir)
    print('Running experiment...')
    model = CoopaModel(play_guessing, env_name, gather_stats, random_behaviour, agents, route_conceptualization)
    times = []
    start_time = time.time()
    period_start = time.time()
    timing_steps = 10000
    for i in range(1, steps + 1):
        if i % timing_steps == 0:
            times.append(time.time() - period_start)
            period_start = time.time()
            time_left = sum(times) / len(times) * ((steps - i) / timing_steps)
            print('Time left {}'.format(str(datetime.timedelta(seconds=time_left))))
        model.step()
    model.finalize()
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
    qgame_map = np.zeros((model.grid.width, model.grid.height))
    for agent in model.agents:
        collisions += agent.stat_dict['obs_game_init']
        items_delivered += agent.stat_dict['items_delivered']
        guessing_played += agent.stat_dict['guessing_game_init']
        option1_selected += agent.stat_dict['option1_selected']
        option2_selected += agent.stat_dict['option2_selected']
        extra_distance += agent.stat_dict['extra_distance']
        collision_map += agent.stat_dict['collision_map']
        qgame_map += agent.stat_dict['q-game_map']
        if create_trees:
            disc_trees = create_graphs(agent.stat_dict['discriminators'][-1][0], agent.stat_dict['memories'][-1][0])
            for j in range(len(disc_trees)):
                chan = 'x' if j == 0 else 'y'
                disc_trees[j].render(filename='run{}_{}_{}'.format(run_id, agent.color, chan),
                                     directory=run_dir, cleanup=True)
        pickle.dump(agent.stat_dict, open(os.path.join(run_dir, '{}.p'.format(agent.unique_id)), 'wb'))
        # asd = pickle.load(open(os.path.join(run_dir, '{}.p'.format(agent.color)), 'rb'))

    pickle.dump(model.place_games, open(os.path.join(run_dir, 'place_games.p'), 'wb'))
    pickle.dump(model.query_games, open(os.path.join(run_dir, 'query_games.p'), 'wb'))

    result_str += 'Collisions: {}\n'.format(collisions)
    result_str += 'Items delivered: {}\n'.format(items_delivered)
    result_str += 'Guessing played: {}\n'.format(guessing_played)
    result_str += 'Option 1 selected: {}\n'.format(option1_selected)
    result_str += 'Option 2 selected: {}\n'.format(option2_selected)
    result_str += 'Extra distance: {}\n'.format(extra_distance)

    with open(os.path.join(run_dir, 'run{}.txt'.format(run_id)), 'w') as text_file:
        print(result_str, file=text_file)

    print(result_str)
    print('Simulation took: {}'.format(str(datetime.timedelta(seconds=time.time() - start_time))))
    print()
    return items_delivered, collisions, collision_map, qgame_map


if __name__ == "__main__":
    np.set_printoptions(suppress=True)
    items_delivered = []
    collisions = []
    collision_maps = []
    qgame_maps = []
    times = []
    runs = 2

    # PARAMS
    params = {'play_guessing': False,
              'gather_stats': True,
              'random_behaviour': True,
              'steps': 50000,
              'create_trees': False,
              'agents': 4,
              'env_name': 'beer_only',              #default, beer, beer_only, double
              'route_conceptualization': 'hack2'}   #hack1, hack2, conceptualize
    pprint.pprint(params)

    date_time = time.strftime("%d-%m-%y_%H-%M-%S")
    rand = 'random' if params['random_behaviour'] else 'shortest'
    lang = 'lang' if params['play_guessing'] else 'prelang'
    # directory = r'D:\resultit\restricted_shelves\extended\results_{}_{}_{}'.format(date_time, rand, lang)
    # directory = r'D:\resultit\restricted_shelves\results_{}_{}_{}'.format(date_time, rand, lang)
    directory = 'results/results_{}_{}_{}'.format(date_time, rand, lang)
    os.makedirs(directory)
    print(directory)

    # Save params to file
    with open(os.path.join(directory, 'params.txt'), 'w') as text_file:
        pprint.pprint(params, stream=text_file)

    for i in range(1, runs + 1):
        start_time = time.time()
        print('Starting run {}'.format(i))
        run_delivered, run_collisions, run_collision_map, run_qgame_map = run_experiment(i, directory=directory, **params)
        items_delivered.append(run_delivered)
        collisions.append(run_collisions)
        collision_maps.append(run_collision_map)
        qgame_maps.append(run_qgame_map)
        times.append(time.time() - start_time)
        time_left = sum(times) / len(times) * (runs - i)
        print('Finished run, time left {}'.format(str(datetime.timedelta(seconds=time_left))))
        print()

    model = CoopaModel(False, params['env_name'])
    collision_map = np.rot90(sum(collision_maps)) / runs
    qgame_map = np.rot90(sum(qgame_maps)) / runs
    create_heatmap(collision_map, model.grid, os.path.join(directory, 'collision_map.pdf'))
    create_heatmap(qgame_map, model.grid, os.path.join(directory, 'qgame_map.pdf'))

    with open(os.path.join(directory, 'final.txt'), 'w') as text_file:
        print('Delivered: {}, avg: {}'.format(items_delivered, np.mean(items_delivered)), file=text_file)
        print('Collisions: {}, avg: {}\n'.format(collisions, np.mean(collisions)), file=text_file)
        print(collision_map)
    # print(resources_delivered)
    # print(collisions)

    print('{}, finished'.format(directory))
    pprint.pprint(params)
