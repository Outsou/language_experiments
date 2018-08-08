from mesa import Agent
from objects import Resource, DropPoint
import numpy as np
from search.astar import astar
from memory import MFAssociationMemory
from objects import Wall
import random
import math
from disc_tree import DiscriminationTree


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
        self.importance_threshold = 5
        self.x_tree = DiscriminationTree((0, 9))
        self.y_tree = DiscriminationTree((0, 17))
        self.last_disc_form = None
        self.avoidable_objs = None
        self.last_discriminator = None
        self.last_meaning = None
        self.stat_dict = {'obs_game_init': 0,
                          'travel_distance': 0,
                          'resources_delivered': 0}
        self.map = np.copy(self.model.map)

    def _find_nearest(self, objects, env_map):
        best_path = astar(env_map, self.pos, objects[0].pos, False)[1:]
        min_dist = len(best_path)
        for obj in objects[1:]:
            path = astar(env_map, self.pos, obj.pos, False)[1:]
            dist = len(path)
            if dist > 0 and dist < min_dist:
                min_dist = dist
                best_path = path
        return best_path

    def _update_map(self):
        map = np.copy(self.model.map)
        if self.avoidable_objs is not None:
            for obj in self.avoidable_objs:
                map[obj] = 1
        self.map = map

    def _find_nearest_resource(self):
        path = self._find_nearest(self.model.resources, self.map)
        self._path = path
        self._state = 'moving'

    def _get_highest_meaning_on_path(self):
        max_meaning = None
        max_utility = -math.inf
        for pos in self._path:
            meaning = self._get_neighborhood(pos)
            utility = self.memory.get_utility(meaning)
            if utility is not None and abs(utility) > max_utility:
                max_utility = abs(utility)
                max_meaning = meaning
        return max_meaning

    def _find_nearest_drop_point(self):
        drop_points = [dp for dp in self.model.drop_points if dp.color == self._resource_color]
        path = self._find_nearest(drop_points, self.map)
        self._path = path
        meaning = self._get_highest_meaning_on_path()
        if meaning is not None:
            self._play_guessing_game(meaning)
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
                    self.stat_dict['resources_delivered'] += 1
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

    def observational_transmit(self, form):
        meaning = self._get_neighborhood(self.pos)
        self.memory.strengthen_meaning(meaning, form)

    def guessing_transmit(self, meaning_form, disc_form):
        self.last_disc_form = disc_form
        self.last_discriminator = None
        self.avoidable_objs = None
        meaning = self.memory.get_meaning(meaning_form)
        self.last_meaning = meaning
        if meaning is None:
            return
        discriminator = self.memory.get_meaning(disc_form)
        if discriminator is None:
            return
        self.last_discriminator = discriminator
        objects = self._get_objects(meaning)
        disc_objects = []
        low, high = discriminator.range
        for obj in objects:
            if low <= obj[0] <= high:
                disc_objects.append(obj)
        if len(disc_objects) > 0:
            self.avoidable_objs = disc_objects

    def _get_relevant_discriminator(self, meaning):
        objects = self._get_objects(meaning)
        discriminators = {}
        relevant_discriminator = None
        for obj in objects:
            discriminator = self.x_tree.discriminate(obj[0])
            if discriminator not in discriminators:
                discriminators[discriminator] = []
            discriminators[discriminator].append(obj)
            if obj == self.pos:
                relevant_discriminator = discriminator
        if len(discriminators.keys()) < 2:
            return None
        return relevant_discriminator

    def _handle_collision(self):
        if self.last_disc_form is None:
            return
        meaning = self._get_neighborhood(self.pos)
        if meaning != self.last_meaning:
            return
        relevant_discriminator = self._get_relevant_discriminator(meaning)
        if relevant_discriminator is None:
            # Failed to discriminate
            self._grow_tree()
            return
        if not self.memory.is_associated(relevant_discriminator, self.last_disc_form):
            self.memory.create_association(relevant_discriminator, self.last_disc_form)
        self.memory.strengthen_meaning(relevant_discriminator, self.last_disc_form)

    def _get_neighborhood(self, pos):
        neighborhood = []
        for x in range(pos[0] - 1, pos[0] + 2):
            neighborhood.append([])
            for y in range(pos[1] - 1, pos[1] + 2):
                neighborhood[-1].append(SYMBOLS[type(self.model.grid[x][y])])
        neighborhood[1][1] = SYMBOLS['self']
        if self.state_rotation:
            neighborhood = self._rotate_state(neighborhood)
        return tuple(tuple(x) for x in neighborhood)

    def _rotate_state(self, state):
        state = np.array(state)
        if self.heading_x == 1:
            state = np.rot90(state)
        elif self.heading_y == -1:
            state = np.rot90(state, 2)
        elif self.heading_x == -1:
            state = np.rot90(state, 3)
        return state

    def _get_objects(self, meaning):
        objects = []
        shape = self.model.map.shape
        for x in range(1, shape[0] - 1):
            for y in range(1, shape[1] - 1):
                neighborhood = self._get_neighborhood((x, y))
                if neighborhood == meaning:
                    objects.append((x, y))
        return objects

    def _discriminate(self, all_objects, topic_objects):
        discrimination_dict = {}
        for obj in all_objects:
            discriminator = self.x_tree.discriminate(obj[0])
            if discriminator not in discrimination_dict:
                discrimination_dict[discriminator] = set()
            discrimination_dict[discriminator].add(obj)
        topic_set = set(topic_objects)
        for discriminator, objs in discrimination_dict.items():
            if objs == topic_set:
                return discriminator
        # Discrimination failed
        self.x_tree.grow()
        return None

    def _play_guessing_game(self, meaning):
        meaning_form = self.memory.get_form(meaning)
        objects = self._get_objects(meaning)
        topic_objects = [obj for obj in objects if obj in self._path]
        discriminator = self._discriminate(objects, topic_objects)
        disc_form = self.memory.get_form(discriminator)
        if disc_form is None:
            disc_form = self.memory.invent_form()
            self.memory.create_association(discriminator, disc_form)
        for agent in self.model.agents:
            if agent != self:
                agent.guessing_transmit(meaning_form, disc_form)
                self._update_map()

    def _play_observational_game(self, utility):
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False, radius=1)
        meaning = self._get_neighborhood(self.pos)
        form = self.memory.get_form(meaning)
        if form is None:
            form = self.memory.invent_form()
            self.memory.create_association(meaning, form)
        self.memory.strengthen_form(meaning, form, utility)
        for neighbor in neighbors:
            if type(neighbor) is AgentBasic:
                neighbor.observational_transmit(form)

    def _reroute(self):
        x, y = self._path[0]
        env_map = np.copy(self.model.map)
        env_map[x][y] = 1
        end_x, end_y = self._path[-1]
        if type(self.model.grid[end_x][end_y]) is DropPoint:
            drop_points = [dp for dp in self.model.drop_points if dp.color == self._resource_color]
            new_path = self._find_nearest(drop_points, env_map)
        else:
            new_path = astar(env_map, self.pos, self._path[-1], False)[1:]
        return new_path

    def _grow_tree(self):
        if self.last_disc_form is None:
            return
        self.x_tree.grow()

    def finish_move(self, change_path):
        old_pos = self.pos
        if change_path or (len(self._path) > 1 and not self.model.grid.is_cell_empty(self._path[0])):
            new_path = self._reroute()
            if len(new_path) == 0:
                return
            if len(new_path) - len(self._path) > self.importance_threshold:
                self._update_direction(old_pos, self._path[0])
                self._play_observational_game(len(self._path) - len(new_path))
                self.stat_dict['obs_game_init'] += 1
                self._handle_collision()
            self._path = new_path
        self.model.grid.move_agent(self, self._path[0])
        self.stat_dict['travel_distance'] += 1
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
