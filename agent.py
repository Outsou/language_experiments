from mesa import Agent
from objects import Resource, DropPoint
import numpy as np
from search.astar import astar
from memory import MFAssociationMemory
from objects import Wall
import random


class AgentBasic(Agent):
    def __init__(self, unique_id, model, color, state_rotation=False):
        super().__init__(unique_id, model)
        self.state_rotation = state_rotation
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
        self.memory = MFAssociationMemory()
        self.heading_x = 1
        self.heading_y = 0
        self.importance_threshold = 7

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
        self._path = astar(self.model.map, self.pos, self._find_nearest(self.model.resources).pos, False)[1:]
        self._state = 'moving'

    def _find_nearest_drop_point(self):
        drop_points = [dp for dp in self.model.drop_points if dp.color == self._resource_color]
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
        neighbors = self.model.grid.get_neighbors(self.pos, moore=False, include_center=False, radius=1)
        if self._resource_count < 1:
            self._pick(neighbors)
        else:
            self._drop(neighbors)

    def transmit_form(self, form):
        meaning = self._get_state()
        self.memory.strengthen_meaning(meaning, form)

    def _get_state(self):
        state = []
        for x in range(self.pos[0] - 1, self.pos[0] + 2):
            state.append([])
            for y in range(self.pos[1] - 1, self.pos[1] + 2):
                state[-1].append(SYMBOLS[type(self.model.grid[x][y])])
        state[1][1] = SYMBOLS['self']
        if self.state_rotation:
            state = self._rotate_state(state)
        return tuple(tuple(x) for x in state)

    def _rotate_state(self, state):
        state = np.array(state)
        if self.heading_x == 1:
            state = np.rot90(state)
        elif self.heading_y == -1:
            state = np.rot90(state, 2)
        elif self.heading_x == -1:
            state = np.rot90(state, 3)
        return state

    def _speak(self, utility):
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False, radius=1)
        meaning = self._get_state()
        form = self.memory.get_form(meaning)
        if form is None:
            form = self.memory.invent_form()
            self.memory.create_association(meaning, form)
        self.memory.strengthen_form(meaning, form, utility)
        for neighbor in neighbors:
            if type(neighbor) is AgentBasic:
                neighbor.transmit_form(form)

    def _reroute(self):
        x, y = self._path[0]
        env_map = np.copy(self.model.map)
        env_map[x][y] = 1
        new_path = astar(env_map, self.pos, self._path[-1], False)[1:]
        return new_path

    def finish_move(self, change_path):
        old_pos = self.pos
        if change_path or (len(self._path) > 1 and not self.model.grid.is_cell_empty(self._path[0])):
            new_path = self._reroute()
            if len(new_path) == 0:
                return
            if len(new_path) - len(self._path) > self.importance_threshold:
                self._update_direction(old_pos, self._path[0])
                self._speak(len(self._path) - len(new_path))
            self._path = new_path
        self.model.grid.move_agent(self, self._path[0])
        del self._path[0]
        if len(self._path) < 2:
            self._state = 'destination_reached'
        self._update_direction(old_pos, self.pos)

    def _update_direction(self, old_pos, new_pos):
        if old_pos[0] < new_pos[0]:
            # Going right
            self.heading_x = 1
            self.heading_y = 0
        elif old_pos[0] > new_pos[0]:
            # Going left
            self.heading_x = -1
            self.heading_y = 0
        elif old_pos[1] < new_pos[1]:
            # Going up
            self.heading_x = 0
            self.heading_y = 1
        elif old_pos[1] > new_pos[1]:
            # Going down
            self.heading_x = 0
            self.heading_y = -1

    def get_reroute_length(self):
        return len(self._reroute())

    def step(self):
        while self._state in self._fast_states:
            self._actions[self._state]()
        self._actions[self._state]()
        # print('STATE: {}'.format(self._state))


SYMBOLS = {
    # AgentBasic: 'A',
    AgentBasic: '.',
    Wall: 'W',
    Resource: 'R',
    DropPoint: 'D',
    type(None): '.',
    'self': 'X'
}
