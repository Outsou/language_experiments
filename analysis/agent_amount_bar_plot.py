from utils import get_dirs_in_path
import ast
import os
import re
import numpy as np
import matplotlib.pyplot as plt
import shutil

if __name__ == '__main__':
    result_path = r'/home/ottohant/Desktop/agent_amounts'
    analysis_dir = 'agent_amount_analysis'

    shutil.rmtree(analysis_dir, ignore_errors=True)
    print('')
    os.mkdir(analysis_dir)

    dirs = sorted(get_dirs_in_path(result_path))
    regex = re.compile('\[.*?\]')
    deliveries_dict = {}
    pass
    for dir in dirs:
        with open(os.path.join(dir, 'params.txt'), 'r') as file:
            params_s = file.read().replace('\n', '')
        param_dict = ast.literal_eval(params_s)
        agent_amount = param_dict['agents']

        with open(os.path.join(dir, 'final.txt'), 'r') as file:
            final_s = file.read().replace('\n', '')
        deliveries_s = regex.findall(final_s)[0]
        deliveries_list = ast.literal_eval(deliveries_s)

        if agent_amount not in deliveries_dict:
            deliveries_dict[agent_amount] = {'hack2': None, 'conceptualize': None}
        deliveries_dict[agent_amount][param_dict['route_conceptualization']] = \
            sum(deliveries_list) / len(deliveries_list) / agent_amount

    optimal = []
    language = []
    agent_amounts = list(range(min(deliveries_dict.keys()), max(deliveries_dict.keys()) + 1))
    for amount in agent_amounts:
        optimal.append(deliveries_dict[amount]['hack2'])
        language.append(deliveries_dict[amount]['conceptualize'])

    fig, ax = plt.subplots()
    index = np.arange(len(optimal))
    bar_width = 0.35
    opacity = 1

    rects1 = ax.bar(index, optimal, bar_width,
                    alpha=opacity, color='b',
                    label='Circling behaviour')

    rects1 = ax.bar(index + bar_width, language, bar_width,
                    alpha=opacity, color='r',
                    label='Language')

    ax.set_xlabel('Amount of agents')
    ax.set_ylabel('Deliveries')
    # ax.set_title('Scores by group and gender')
    ax.set_xticks(index + bar_width / 2)
    ax.set_xticklabels(agent_amounts)
    ax.legend()

    fig.tight_layout()
    plt.savefig(os.path.join(analysis_dir, 'amounts_deliveries.pdf'))

    pass