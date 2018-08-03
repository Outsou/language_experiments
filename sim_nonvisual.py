from coopa_model import CoopaModel
from utils import print_state
import time


def test2():
    print('Running Test2...')
    model = CoopaModel(60, 60)
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
        for meaning, form in agent.memory.association_dict.items():
            print_state(meaning)
            print(form)
            print()
        print('-----------------------------')
    print('Simulation took: {}'.format(time.time() - start_time))


if __name__ == "__main__":
    test2()
