from mesa import Agent
import random


class Wall(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

class Resource(Agent):
    def __init__(self, unique_id, model, color, spawn_points):
        super().__init__(unique_id, model)
        self._color = color
        self._spawn_points = spawn_points

    @property
    def color(self):
        return self._color

    def respawn(self):
        self.model.grid.remove_agent(self)
        color, point = random.choice(list(self._spawn_points.items()))
        self._color = color
        self.model.grid.place_agent(self, point)

class DropPoint(Agent):
    def __init__(self, unique_id, model, color):
        super().__init__(unique_id, model)
        self.color = color
        self._resource_count = 0

    def add_resources(self, amount):
        self._resource_count += 1

class Shelf(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

class ActionCenter(Agent):
    def __init__(self, unique_id, model, shelves):
        super().__init__(unique_id, model)
        self._shelves = shelves
        self._items = 0

    def drop_item(self):
        self._items += 1

    def get_mission(self):
        return random.choice(self._shelves)
