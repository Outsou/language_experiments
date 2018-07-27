from mesa import Model
from mesa.time import RandomActivation
from mesa.space import SingleGrid
from message_dispatcher import MessageDispatcher
from layout import Layout
from objects import Resource, DropPoint, Wall
from mesa.datacollection import DataCollector
from agent import AgentBasic
from search.util import build_map
import random


class CoopaModel(Model):
    """A model with some number of agents."""

    def __init__(self, width, height):
        self.running = True
        self.grid = SingleGrid(width, height, False)  # True=toroidal
        self.schedule = RandomActivation(self)
        self.message_dispatcher = MessageDispatcher()
        self.layout = Layout()
        self.datacollector = DataCollector()  # An agent attribute
        self.drop_points = []
        self.resources = []
        self.move_queue = []

        self.layout.draw(self.grid)

        # Spawn agents
        a = AgentBasic(0, self, 'green')
        self.schedule.add(a)
        self.grid.position_agent(a, 4, 2)

        a = AgentBasic(1, self, 'black')
        self.schedule.add(a)
        self.grid.position_agent(a, 4, 15)

        # Spawn drop points
        drop_point = DropPoint(2, self, 'blue')
        self.grid.place_agent(drop_point, (1, 2))
        self.drop_points.append(drop_point)

        drop_point = DropPoint(3, self, 'blue')
        self.grid.place_agent(drop_point, (8, 2))
        self.drop_points.append(drop_point)

        drop_point = DropPoint(4, self, 'red')
        self.grid.place_agent(drop_point, (1, 15))
        self.drop_points.append(drop_point)

        drop_point = DropPoint(5, self, 'red')
        self.grid.place_agent(drop_point, (8, 15))
        self.drop_points.append(drop_point)

        # Spawn resources
        resource = Resource(6, self, 'red', ((1, 3), (8, 3)))
        self.grid.place_agent(resource, (1, 3))
        self.resources.append(resource)

        resource = Resource(7, self, 'blue', ((1, 14), (8, 14)))
        self.grid.place_agent(resource, (1, 14))
        self.resources.append(resource)

        self.map = build_map(self.grid, (Wall, DropPoint))
        self.map[1][3] = 1
        self.map[8][3] = 1
        self.map[1][14] = 1
        self.map[8][14] = 1

    def step(self):
        self.schedule.step()
        self.move_agents()

    def move_agents(self):
        if len(self.move_queue) > 1:
            A, B, agent1 = self.move_queue[0]
            C, D, agent2 = self.move_queue[1]
            agents = [agent1, agent2]
            random.shuffle(agents)
            if A == D and B == C:
                agents[0].finish_move(True)
                agents[1].finish_move(False)
            elif  B == D:
                agents[1].finish_move(False)
                agents[0].finish_move(True)
            else:
                if B == C:
                    agent2.finish_move(False)
                    agent1.finish_move(False)
                else:
                    agent1.finish_move(False)
                    agent2.finish_move(False)

        elif len(self.move_queue) == 1:
            self.move_queue[0][2].finish_move(False)
        self.move_queue = []

    def queue_move(self, start, end, agent):
        self.move_queue.append((start, end, agent))
