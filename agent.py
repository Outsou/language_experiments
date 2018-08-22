from mesa import Agent
from objects import Resource, DropPoint
import numpy as np
from search.astar import astar
from memory import MFAssociationMemory
from objects import Wall
import random
import math
from disc_tree import Discriminator
from utils import create_graphs


class AgentBasic(Agent):
    def __init__(self, unique_id, model, color, neighborhood_rotation=False, guessing_game=True):
        super().__init__(unique_id, model)
        self._guessing_game = guessing_game
        self.neighborhood_rotation = neighborhood_rotation
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
        self.importance_threshold = 8
        self.discriminator = Discriminator([(0, 9), (0, 17)])
        self.last_disc_form = None
        self.avoidable_objs = None
        self.last_discriminator = None
        self.last_meaning = None
        self.stat_dict = {'obs_game_init': 0,
                          'travel_distance': 0,
                          'resources_delivered': 0,
                          'disc_trees': []}
        self.map = np.copy(self.model.map)
        self.collided = None

    def _find_nearest(self, objects, env_map):
        '''Finds the nearest object in objects and returns the path to it.'''
        best_path = []
        min_dist = math.inf
        for obj in objects:
            path = astar(env_map, self.pos, obj.pos, False)[1:]
            dist = len(path)
            if 0 < dist < min_dist:
                min_dist = dist
                best_path = path
        return best_path

    def _update_map(self):
        '''Adds blockages to the maps for cells the agent thinks should be avoided.'''
        map = np.copy(self.model.map)
        if self.avoidable_objs is not None:
            for obj in self.avoidable_objs:
                map[obj] = 1
        self.map = map

    def _find_nearest_resource(self):
        '''Finds the nearest resource and sets the agent's course toward it.'''
        path = self._find_nearest(self.model.resources, self.map)
        if len(path) < 1:
            self.avoidable_objs = None
            self._update_map()
            path = self._find_nearest(self.model.resources, self.map)
        self._path = path
        self._state = 'moving'

    def _find_nearest_drop_point(self):
        '''Finds the nearest eligible drop point and sets the agent's course toward it.'''
        drop_points = [dp for dp in self.model.drop_points if dp.color == self._resource_color]
        path = self._find_nearest(drop_points, self.map)
        if len(path) < 1:
            self.avoidable_objs = None
            self._update_map()
            path = self._find_nearest(drop_points, self.map)
        self._path = path
        if self._guessing_game:
            meaning = self._get_highest_meaning_on_path()
            if meaning is not None:
                self._play_guessing_game(meaning)
        self._state = 'moving'

    def _get_highest_meaning_on_path(self):
        '''Finds out the most important thing on the agent's path.
        Importance is determined by absolute value of a meaning's perceived utility.'''
        max_meaning = None
        max_utility = -math.inf
        for pos in self._path:
            meaning = self._get_neighborhood(pos)
            utility = self.memory.get_utility(meaning)
            if utility is not None and abs(utility) > max_utility:
                max_utility = abs(utility)
                max_meaning = meaning
        return max_meaning

    def start_observational_game(self, hearer, reroute, utility):
        if abs(utility) >= self.importance_threshold:
            self._play_observational_game(utility, hearer)
            self._handle_collision()
        self._path = reroute

    def _game_check(self, neighbor):
        if len(neighbor._path) > 0 and neighbor._path[0] == self.pos:
            own_reroute = self._reroute()
            own_utility = len(self._path) - len(own_reroute)
            neighbor_reroute = neighbor._reroute()
            neighbor_utility = len(neighbor._path) - len(neighbor_reroute)
            if len(own_reroute) > 0 and own_utility >= neighbor_utility:
                if abs(own_utility) >= self.importance_threshold:
                    self._play_observational_game(own_utility, neighbor)
                    self._handle_collision()
                self._path = own_reroute
            # elif len(own_reroute) == 0 and len(neighbor_reroute) == 0:
            #     self._change_destination()
            else:
                neighbor.start_observational_game(self, neighbor_reroute, neighbor_utility)

    def _move(self):
        '''Moves the agent and initiates observational game if needed.'''
        if len(self._path) > 1:
            x, y = self._path[0]
            if self.model.grid.is_cell_empty(self._path[0]):
                old_pos = self.pos
                self.model.grid.move_agent(self, self._path[0])
                self.stat_dict['travel_distance'] += 1
                del self._path[0]
                if len(self._path) < 2:
                    self._state = 'destination_reached'
                self._update_direction(old_pos, self.pos)
            elif type(self.model.grid[x][y]) is AgentBasic:
                self._game_check(self.model.grid[x][y])
        else:
            self._state = 'destination_reached'

    def _pick(self, neighbors):
        '''Picks up a resource.'''
        for neighbor in neighbors:
            if type(neighbor) is Resource:
                self._resource_count += 1
                self._resource_color = neighbor.color
                self._state = 'has_resource'
                neighbor.respawn()
        if self._resource_count < 1:
            self._state = 'no_resource'
        else:
            self._state = 'has_resource'

    def _drop(self, neighbors):
        '''Drops a resource at a drop point.'''
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
        '''Determines whether to pick up or drop a resrouce.'''
        neighbors = self.model.grid.get_neighbors(self.pos, moore=False, include_center=False, radius=1)
        if self._resource_count < 1:
            self._pick(neighbors)
        else:
            self._drop(neighbors)

    def observational_transmit(self, form):
        '''Speaker uses this to transmit form to hearer in the observational game.'''
        meaning = self._get_neighborhood(self.pos)
        self.memory.strengthen_meaning(meaning, form)

    def guessing_transmit(self, meaning_form, disc_form):
        '''Speaker uses this to transmit forms to the hearer in the guessing game.'''
        if self.collided is False and self.last_discriminator is not None and self.avoidable_objs is not None:
            self.memory.strengthen_meaning(self.last_discriminator, self.last_disc_form)

        self.last_disc_form = disc_form
        self.last_discriminator = None
        self.avoidable_objs = None
        self.collided = False
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
            if low <= obj[discriminator.channel] <= high:
                disc_objects.append(obj)
        if len(disc_objects) > 0:
            self.avoidable_objs = disc_objects
            self._update_map()

    def _handle_collision(self):
        '''Handles learning when failure in communication has resulted in a collision.'''
        if self.last_disc_form is None:
            return

        meaning = self._get_neighborhood(self.pos)
        if meaning != self.last_meaning:
            return

        self.collided = True

        objects = self._get_objects(meaning)
        relevant_discriminators = self.discriminator.get_relevant_discriminators(self.pos, objects)
        if self.last_discriminator is not None:
            if self.last_discriminator in relevant_discriminators:
                relevant_discriminators.remove(self.last_discriminator)
            self.memory.weaken_association(self.last_discriminator, self.last_disc_form)

        if len(relevant_discriminators) < 1:
            self.discriminator.grow()
            return

        relevant_discriminator = random.choice(relevant_discriminators)

        if not self.memory.is_associated(relevant_discriminator, self.last_disc_form):
            self.memory.create_association(relevant_discriminator, self.last_disc_form)
        self.memory.strengthen_meaning(relevant_discriminator, self.last_disc_form)

    def _get_neighborhood(self, pos):
        '''Returns the 3x3 grid around the agent.'''
        neighborhood = []
        for x in range(pos[0] - 1, pos[0] + 2):
            neighborhood.append([])
            for y in range(pos[1] - 1, pos[1] + 2):
                neighborhood[-1].append(SYMBOLS[type(self.model.grid[x][y])])
        neighborhood[1][1] = SYMBOLS['self']
        if self.neighborhood_rotation:
            neighborhood = self._rotate_neighborhood(neighborhood)
        return tuple(tuple(x) for x in neighborhood)

    def _rotate_neighborhood(self, neighborhood):
        '''Rotates the neighborhood so that it is perceived based on the direction the agent is facing.'''
        neighborhood = np.array(neighborhood)
        if self.heading_x == 1:
            neighborhood = np.rot90(neighborhood)
        elif self.heading_y == -1:
            neighborhood = np.rot90(neighborhood, 2)
        elif self.heading_x == -1:
            neighborhood = np.rot90(neighborhood, 3)
        return neighborhood

    def _get_objects(self, meaning):
        '''Returns all the cells on the map that correspond to the meaning.'''
        objects = []
        shape = self.model.map.shape
        for x in range(1, shape[0] - 1):
            for y in range(1, shape[1] - 1):
                neighborhood = self._get_neighborhood((x, y))
                if neighborhood == meaning:
                    objects.append((x, y))
        return objects

    def _discriminate(self, all_objects, topic_objects):
        '''Finds a discriminator that can discriminate the topic objects from all objects.'''
        discriminator = self.discriminator.discriminate(all_objects, topic_objects)
        if discriminator is None:
            self.discriminator.grow()
        return discriminator

    def _play_guessing_game(self, meaning):
        '''Start the guessing game as the speaker.'''
        meaning_form = self.memory.get_form(meaning)
        objects = self._get_objects(meaning)
        topic_objects = [obj for obj in objects if obj in self._path]
        discriminator = self._discriminate(objects, topic_objects)
        if discriminator is None:
            return
        disc_form = self.memory.get_form(discriminator)
        if disc_form is None:
            disc_form = self.memory.invent_form()
            self.memory.create_association(discriminator, disc_form)
        self.memory.report_form_use(discriminator, disc_form)
        # self.memory.strengthen_form(discriminator, disc_form)
        for agent in self.model.agents:
            if agent != self:
                agent.guessing_transmit(meaning_form, disc_form)

    def _play_observational_game(self, utility, hearer):
        '''Start the observational game as the speaker.'''
        self.stat_dict['obs_game_init'] += 1
        meaning = self._get_neighborhood(self.pos)
        form = self.memory.get_form(meaning)
        if form is None:
            form = self.memory.invent_form()
            self.memory.create_association(meaning, form)
        self.memory.report_form_use(meaning, form)
        self.memory.strengthen_form(meaning, form, utility)
        hearer.observational_transmit(form)

    def _reroute(self):
        '''Finds a new route to destination assuming that the first step in the current route is blocked.'''
        neighborhood = self.model.grid.get_neighbors(self.pos, False)
        env_map = np.copy(self.model.map)
        for neighbor in neighborhood:
            x, y = neighbor.pos
            env_map[x][y] = 1
        end_x, end_y = self._path[-1]
        if type(self.model.grid[end_x][end_y]) is DropPoint:
            drop_points = [dp for dp in self.model.drop_points if dp.color == self._resource_color]
            new_path = self._find_nearest(drop_points, env_map)
        else:
            new_path = astar(env_map, self.pos, self._path[-1], False)[1:]
        return new_path

    def _update_direction(self, old_pos, new_pos):
        '''Changes agent to face it's movement direction.'''
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
        '''Gets the length of the new route if the agent has to reroute.'''
        return len(self._reroute())

    def step(self):
        while self._state in self._fast_states:
            self._actions[self._state]()
        self._actions[self._state]()
        # print('STATE: {}'.format(self._state))

    def finish_step(self):
        self.stat_dict['disc_trees'].append(create_graphs(self.discriminator, self.memory))


# The symbols used to create the 3x3 neighborhood grid.
SYMBOLS = {
    # AgentBasic: 'A',
    AgentBasic: '.',
    Wall: 'W',
    Resource: 'R',
    DropPoint: 'D',
    type(None): '.',
    'self': 'X'
}
