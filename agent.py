from mesa import Agent
from objects import Resource, DropPoint
import random
import numpy as np
from search.astar import astar


class AgentBasic(Agent):
    def __init__(self, unique_id, model, color):
        super().__init__(unique_id, model)
        self._resource_count = 0
        self._resource_color = None
        self._state = 'no_resource'
        self._path = None
        self._actions = {'no_resource': self._find_nearest_resource,
                         'has_resource': self._find_nearest_drop_point,
                         'moving': self._move,
                         'destination_reached': self._pick_or_drop}
        self._fast_states = ['no_resource', 'has_resource']
        self.color = color

    def _find_nearest(self, objects):
        nearest = objects[0]
        min_dist = np.linalg.norm(np.array(self.pos) - np.array(objects[0].pos))
        for obj in objects[1:]:
            dist = np.linalg.norm(np.array(self.pos) - np.array(obj.pos))
            if dist < min_dist:
                nearest = obj
                min_dist = dist
        return nearest

    def _find_nearest_resource(self):
        self._path = astar(self.model.map, self.pos, self._find_nearest(self.model.resources).pos)[1:]
        self._state = 'moving'

    def _find_nearest_drop_point(self):
        drop_points = [dp  for dp in self.model.drop_points if dp.color == self._resource_color]
        self._path = astar(self.model.map, self.pos, self._find_nearest(drop_points).pos, False)[1:]
        self._state = 'moving'

    def _move(self):
        if len(self._path) > 1:
            self.model.queue_move(self.pos, self._path[0], self)
        else:
            self._state = 'destination_reached'

    def _pick(self, neighbors):
        for neighbor in neighbors:
            if type(neighbor) is Resource:
                self._resource_count += 1
                self._resource_color = neighbor.color
                self._state = 'has_resource'
                spawn_points = neighbor.spawn_points
                self.model.grid.remove_agent(neighbor)
                spawn_point = random.choice(spawn_points)
                self.model.grid.place_agent(neighbor, spawn_point)
        if self._resource_count < 1:
            self._state = 'no_resource'
        else:
            self._state = 'has_resource'

    def _drop(self, neighbors):
        for neighbor in neighbors:
            if type(neighbor) is DropPoint:
                if neighbor.color == self._resource_color:
                    neighbor.add_resources(self._resource_count)
                    self._resource_count = 0
                    self._state = 'no_resource'
        if self._resource_count > 0:
            self._state = 'has_resource'
        else:
            self._state= 'no_resource'

    def _pick_or_drop(self):
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False, radius=1)
        if self._resource_count < 1:
            self._pick(neighbors)
        else:
            self._drop(neighbors)

    def finish_move(self, change_path):
        if change_path or (len(self._path) > 1 and not self.model.grid.is_cell_empty(self._path[0])):
            x, y = self._path[0]
            map = np.copy(self.model.map)
            map[x][y] = 1
            new_path = astar(map, self.pos, self._path[-1], False)[1:]
            if len(new_path) == 0:
                return
            self._path = new_path
        self.model.grid.move_agent(self, self._path[0])
        del self._path[0]
        if len(self._path) < 2:
            self._state = 'destination_reached'

    def step(self):
        while self._state in self._fast_states:
            self._actions[self._state]()
        self._actions[self._state]()
        print('STATE: {}'.format(self._state))
