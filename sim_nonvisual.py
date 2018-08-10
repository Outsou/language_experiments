from coopa_model import CoopaModel
from utils import print_state
import time


def test2(run_id):
    print('Running Test2...')
    model = CoopaModel()
    times = []
    start_time = time.time()
    period_start = time.time()
    timing_steps = 10000
    steps = 100000
    for i in range(1, steps + 1):
        if i % timing_steps == 0:
            times.append(time.time() - period_start)
            period_start = time.time()
            print('Time left: {}'.format(sum(times) / len(times) * ((steps - i) / timing_steps)))
        model.step()
    print()
    for agent in model.agents:
        for meaning, form in agent.memory.mf_dict.items():
            if type(meaning) is tuple:
                print_state(meaning)
                print(form)
                print(agent.memory.meaning_stats[meaning])
                print()
        print('-----------------------------')
    print('Simulation took: {}'.format(time.time() - start_time))

    collisions = 0
    travel_distance = 0
    resources_delivered = 0
    for agent in model.agents:
        collisions += agent.stat_dict['obs_game_init']
        travel_distance += agent.stat_dict['travel_distance']
        resources_delivered += agent.stat_dict['resources_delivered']
        for j in range(len(agent.stat_dict['disc_trees'][-1])):
            agent.stat_dict['disc_trees'][-1][j].render(filename='{}_{}_run{}'.format(agent.color, j, run_id), directory='results')
    print('Collisions: {}'.format(collisions))
    print('Travel distance: {}'.format(travel_distance))
    print('Resources delivered: {}'.format(resources_delivered))
    print()
    return resources_delivered, collisions

if __name__ == "__main__":
    resources_delivered = []
    collisions = []
    times = []
    runs = 1
    for i in range(1, runs + 1):
        start_time = time.time()
        print('Starting run {}'.format(i))
        run_delivered, run_collisions = test2(i)
        resources_delivered.append(run_delivered)
        collisions.append(run_collisions)
        times.append(time.time() - start_time)
        print('Finished run, time left {}'.format(sum(times) / len(times) * (runs - i)))
        print()
    print(resources_delivered)
    print(collisions)
