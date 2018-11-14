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


class CoopaModel(Model):
    """A model with some number of agents."""

    def __init__(self, play_guessing):
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

        # Agents
        self.agents = []
        a = AgentBasic(0, self, 'green', guessing_game=play_guessing)
        self.schedule.add(a)
        self.grid.position_agent(a, 4, 9)
        self.agents.append(a)

        a = AgentBasic(0, self, 'blue', guessing_game=play_guessing)
        self.schedule.add(a)
        self.grid.position_agent(a, 2, 9)
        self.agents.append(a)

        # a = AgentBasic(0, self, 'black', guessing_game=play_guessing)
        # self.schedule.add(a)
        # self.grid.position_agent(a, 3, 9)
        # self.agents.append(a)
        #
        # a = AgentBasic(0, self, 'purple', guessing_game=play_guessing)
        # self.schedule.add(a)
        # self.grid.position_agent(a, 5, 9)
        # self.agents.append(a)

    def step(self):
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

    def ask_broadcast(self, place_form, disc_form):
        return True

    # def queue_move(self, start, end, agent):
    #     self.move_queue.append((start, end, agent))
