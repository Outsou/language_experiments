from mesa import Model
from mesa.time import RandomActivation
from mesa.space import SingleGrid
from message_dispatcher import MessageDispatcher
from layout import Layout
from objects import Wall, Shelf, ActionCenter
from mesa.datacollection import DataCollector
from search.util import build_map
from agent import AgentBasic
import random
import numpy as np


class CoopaModel(Model):
    """A model with some number of agents."""

    def __init__(self, play_guessing, gather_stats=False, random_behaviour=False, agents=1):
        self.running = True
        self.grid = SingleGrid(Layout.width, Layout.height, False)  # True=toroidal
        self.schedule = RandomActivation(self)
        self.message_dispatcher = MessageDispatcher()
        self.layout = Layout()
        self.datacollector = DataCollector()  # An agent attribute
        # self.move_queue = []
        self.agents = []
        self.action_center = self.layout.create_world(self, play_guessing)['action_center']
        self.map = build_map(self.grid, (Wall, Shelf, ActionCenter))
        self.not_moved = []
        self.place_games = []
        self.query_games = []
        self.start_time = None

        # Agents
        self.agents = []
        colors = ['blue', 'black', 'green', 'purple', 'red', 'pink']

        for i in range(agents):
            a = AgentBasic(100 + i, self, colors[i], guessing_game=play_guessing,
                           gather_stats=gather_stats, random_behaviour=random_behaviour)
            self.schedule.add(a)
            self.agents.append(a)

        for agent in self.agents:
            self.grid.position_agent(agent)

        np.set_printoptions(linewidth=320)

    def step(self):
        self.start_time = self.schedule.time
        self.schedule.step()
        self.not_moved = [a for a in self.agents]
        random.shuffle(self.not_moved)

        while len(self.not_moved) > 0:
            for agent in self.not_moved:
                if agent.move():
                    self.not_moved.remove(agent)

        self.finish_step()

    def has_agent_moved(self, agent):
        return not agent in self.not_moved

    def finish_step(self):
        for agent in self.agents:
            agent.finish_step()

    def broadcast_question(self, place, place_form, categoriser, disc_form, asker):
        '''Returns False if even one agent opposes the plan. Otherwise True.'''
        game = {'id': asker.unique_id,
                'place': place,
                'place_form': place_form,
                'categoriser': categoriser,
                'disc_form': disc_form,
                'answers': {},
                'time': self.start_time}
        is_free = True

        # Gather answers
        for agent in self.agents:
            if agent is not asker:
                free, hearer_place, hearer_p_form, hearer_categoriser, hearer_c_form \
                    = agent.ask_if_free(place_form, disc_form)
                game['answers'][agent.unique_id] = {'free': free,
                                                    'place': hearer_place,
                                                    'place_form': hearer_p_form,
                                                    'categoriser': hearer_categoriser,
                                                    'categoriser_form': hearer_c_form}
                if not free:
                    is_free = False

        game['free'] = is_free
        self.query_games.append(game)
        return is_free

    def report_place_game(self, game_dict):
        game_dict['time'] = self.start_time
        self.place_games.append(game_dict)

    # def queue_move(self, start, end, agent):
    #     self.move_queue.append((start, end, agent))
