from mesa import Agent
import numpy as np
from search.astar import astar
from memory import MFAssociationMemory
from objects import Wall, ActionCenter, Shelf
import random
import math
from disc_tree import Discriminator
import copy

class AgentBasic(Agent):
    def __init__(self, unique_id, model, color, neighborhood_rotation=False, guessing_game=True, premade_lang=False,
                 utility_threshold=2, gather_stats=False, random_behaviour=False):
        super().__init__(unique_id, model)
        self._guessing_game = guessing_game
        self.neighborhood_rotation = neighborhood_rotation
        self._premade_lang = premade_lang
        self._utility_threshold = utility_threshold
        self._gather_stats = gather_stats
        self._rand_behaviour = random_behaviour
        self._destination = model.action_center.pos
        self._path = None
        self.color = color
        self.memory = MFAssociationMemory()
        self.heading_x = 1
        self.heading_y = 0
        self.discriminator = Discriminator([(0, 1), (0, 1)])
        self.map = np.copy(self.model.map)
        self.stat_dict = {'obs_game_init': 0,
                          'items_delivered': 0,
                          'guessing_game_init': 0,
                          'discriminators': [(copy.deepcopy(self.discriminator), 0)],
                          'memories': [(copy.deepcopy(self.memory), 0)],
                          'option1_selected': 0,
                          'option2_selected': 0,
                          'extra_distance': 0,
                          'collision_map': np.zeros(self.map.shape),
                          'delivery_times': []}
        self._has_item = False
        self._backing_off = False
        self._backing_info = None
        self._age = 0
        self._last_broadcast = None
        self._blocked = None
        self._last_delivery = 0

        # if self._premade_lang:
        #     self.discriminator.grow(0)
        #     self.memory.create_association(self.discriminator.trees[0].root.child1, 'LEFT')
        #     self.memory.strengthen_form(self.discriminator.trees[0].root.child1, 'LEFT')
        #     self.memory.create_association(self.discriminator.trees[0].root.child2, 'RIGHT')
        #     self.memory.strengthen_form(self.discriminator.trees[0].root.child2, 'RIGHT')
        #     self.memory.create_association((('S', 'S', 'S'), ('.', 'X', '.'), ('S', 'S', 'S')), 'CORRIDOR')
        #     self.memory.strengthen_form((('S', 'S', 'S'), ('.', 'X', '.'), ('S', 'S', 'S')), 'CORRIDOR')
        #     self.memory._update_utility((('S', 'S', 'S'), ('.', 'X', '.'), ('S', 'S', 'S')), -100)

        # if self._premade_lang:
        #     self.discriminator.grow(0)
        #     self.discriminator.trees[0].root.child1.grow()
        #     self.memory.create_association(self.discriminator.trees[0].root.child1.child1, 'VERY_LEFT')
        #     self.memory.strengthen_form(self.discriminator.trees[0].root.child1.child1, 'VERY_LEFT')
        #     self.memory.create_association(self.discriminator.trees[0].root.child1.child2, 'SEMI_LEFT')
        #     self.memory.strengthen_form(self.discriminator.trees[0].root.child1.child2, 'SEMI_LEFT')
        #     self.memory.create_association(self.discriminator.trees[0].root.child2, 'RIGHT')
        #     self.memory.strengthen_form(self.discriminator.trees[0].root.child2, 'RIGHT')
        #     self.memory.create_association((('S', 'S', 'S'), ('.', 'X', '.'), ('S', 'S', 'S')), 'CORRIDOR')
        #     self.memory.strengthen_form((('S', 'S', 'S'), ('.', 'X', '.'), ('S', 'S', 'S')), 'CORRIDOR')
        #     self.memory._update_utility((('S', 'S', 'S'), ('.', 'X', '.'), ('S', 'S', 'S')), -100)

        # if self._premade_lang:
        #     self.discriminator.grow(0)
        #     self.discriminator.trees[0].root.child1.grow()
        #     self.discriminator.trees[0].root.child2.grow()
        #     self.memory.create_association(self.discriminator.trees[0].root.child1.child1, 'VERY_LEFT')
        #     self.memory.strengthen_form(self.discriminator.trees[0].root.child1.child1, 'VERY_LEFT')
        #     self.memory.create_association(self.discriminator.trees[0].root.child1.child2, 'SEMI_LEFT')
        #     self.memory.strengthen_form(self.discriminator.trees[0].root.child1.child2, 'SEMI_LEFT')
        #     self.memory.create_association(self.discriminator.trees[0].root.child2.child1, 'SEMI_RIGHT')
        #     self.memory.strengthen_form(self.discriminator.trees[0].root.child2.child1, 'SEMI_RIGHT')
        #     self.memory.create_association(self.discriminator.trees[0].root.child2.child2, 'VERY_RIGHT')
        #     self.memory.strengthen_form(self.discriminator.trees[0].root.child2.child2, 'VERY_RIGHT')
        #     self.memory.create_association((('S', 'S', 'S'), ('.', 'X', '.'), ('S', 'S', 'S')), 'CORRIDOR')
        #     self.memory.strengthen_form((('S', 'S', 'S'), ('.', 'X', '.'), ('S', 'S', 'S')), 'CORRIDOR')
        #     self.memory._update_utility((('S', 'S', 'S'), ('.', 'X', '.'), ('S', 'S', 'S')), -100)

        if self._premade_lang:
            self.discriminator.grow(0)
            self.discriminator.grow(1)
            self.discriminator.trees[0].root.child1.grow()
            self.discriminator.trees[0].root.child2.grow()
            self.memory.create_association(self.discriminator.trees[1].root.child1, 'DOWN')
            self.memory.strengthen_form(self.discriminator.trees[1].root.child1, 'DOWN')
            self.memory.create_association(self.discriminator.trees[1].root.child2, 'UP')
            self.memory.strengthen_form(self.discriminator.trees[1].root.child2, 'UP')
            self.memory.create_association(self.discriminator.trees[0].root.child1.child1, 'VERY_LEFT')
            self.memory.strengthen_form(self.discriminator.trees[0].root.child1.child1, 'VERY_LEFT')
            self.memory.create_association(self.discriminator.trees[0].root.child1.child2, 'SEMI_LEFT')
            self.memory.strengthen_form(self.discriminator.trees[0].root.child1.child2, 'SEMI_LEFT')
            self.memory.create_association(self.discriminator.trees[0].root.child2.child1, 'SEMI_RIGHT')
            self.memory.strengthen_form(self.discriminator.trees[0].root.child2.child1, 'SEMI_RIGHT')
            self.memory.create_association(self.discriminator.trees[0].root.child2.child2, 'VERY_RIGHT')
            self.memory.strengthen_form(self.discriminator.trees[0].root.child2.child2, 'VERY_RIGHT')
            self.memory.create_association((('S', 'S', 'S'), ('.', 'X', '.'), ('S', 'S', 'S')), 'CORRIDOR')
            self.memory.strengthen_form((('S', 'S', 'S'), ('.', 'X', '.'), ('S', 'S', 'S')), 'CORRIDOR')
            self.memory._update_utility((('S', 'S', 'S'), ('.', 'X', '.'), ('S', 'S', 'S')), -100)

    def _get_highest_meaning_on_path(self, path):
        '''Finds out the most important thing on the agent's path.
        Importance is determined by absolute value of a meaning's perceived utility.'''
        max_meaning = None
        max_utility = -math.inf
        for pos in path:
            meaning = self._get_neighborhood(pos)
            utility = self.memory.get_utility(meaning)
            if utility is not None and abs(utility) > max_utility:
                max_utility = abs(utility)
                max_meaning = meaning
        # if max_utility < self._utility_threshold:
        #     return None
        return max_meaning

    def _get_free_neighbors(self):
        '''Returns the coordinates of the cells around the agent that are empty.'''
        free = []
        x, y = self.pos
        for cell in [(x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y)]:
            if self.model.grid.is_cell_empty(cell):
                free.append(cell)
        return free

    def _handle_backing_move(self):
        '''Used to move when the agent is backing, i.e. giving way to another agent.'''
        neighbors = self.model.grid.get_neighbors(self.pos, moore=False, include_center=False, radius=1)
        self.map = np.copy(self.model.map)
        for neighbor in neighbors:
            x, y = neighbor.pos
            self.map[x][y] = 1
        path = self._reroute()
        if len(path) > 0:
            # Route is clear, stop backing
            self._path = path
            self._backing_off = False
            utility = self._backing_info['start_age'] - self._age
            self.memory._update_utility(self._backing_info['meaning'], utility)
        else:
            # Route not clear, choose random move
            movement_options = self._get_free_neighbors()
            x_dist = abs(self.pos[0] - self.model.action_center.pos[0])
            y_dist = abs(self.pos[1] - self.model.action_center.pos[1])
            movement_options = [x for x in movement_options
                                if abs(x[0] - self.model.action_center.pos[0]) < x_dist
                                or abs(x[1] - self.model.action_center.pos[1]) < y_dist]
            if len(movement_options) > 0:
                old_pos = self.pos
                self.model.grid.move_agent(self, random.choice(movement_options))
                self._update_direction(old_pos, self.pos)
            return True
        return False

    def _handle_normal_move(self):
        '''Used to move normally, i.e. when the agent is not giving way to another agent.
        Starts backing movement and an observational game if needed.'''
        x, y = self._path[0]
        if self.model.grid.is_cell_empty(self._path[0]):
            # Path is free, just move
            old_pos = self.pos
            self.model.grid.move_agent(self, self._path[0])
            del self._path[0]
            self._update_direction(old_pos, self.pos)
            return True

        # Path is not free
        neighbor = self.model.grid[x][y]
        if type(neighbor) is AgentBasic:
            reroute = self._reroute()
            if len(reroute) > 0:
                self._path = reroute
                old_pos = self.pos
                self.model.grid.move_agent(self, self._path[0])
                del self._path[0]
                self._update_direction(old_pos, self.pos)
                return True
            # There is an agent in the way, check if game should be played
            if not self._has_item:
                self.stat_dict['collision_map'][self.pos] += 1
                self._backing_off = True
                meaning = self._play_observational_game(neighbor)
                self._backing_info = {'start_age': self._age,
                                      'meaning': meaning}
            elif self.model.has_agent_moved(neighbor):
                return True
        return False

    def move(self):
        '''Moves the agent.'''
        if len(self._path) > 1:
            if self._backing_off:
                return self._handle_backing_move()
            else:
                return self._handle_normal_move()
        return True

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

    def _normalise(self, objects):
        '''Normalises a list of cell coordinates.'''
        x_list, y_list = zip(*objects)
        min_x = min(x_list)
        min_y = min(y_list)
        range_x = max(x_list) - min_x
        range_y = max(y_list) - min_y
        if range_x == 0:
            range_x = 1
        if range_y == 0:
            range_y = 1
        return [((x - min_x)/range_x, (y - min_y)/range_y) for x, y in objects]

    def _discriminate(self, all_objects, topic_objects, disc_objects):
        '''Finds a categoriser that can discriminate the topic objects from all objects.'''
        all_objects = set(all_objects)
        topic_objects = set(topic_objects)
        if all_objects == topic_objects:
            return None
        categoriser = self.discriminator.set_discriminate(all_objects, topic_objects, disc_objects)
        if categoriser is None:
            self.discriminator.grow(disc_objects=disc_objects, topic_objects=topic_objects)
            if self._gather_stats:
                self.stat_dict['discriminators'].append((copy.deepcopy(self.discriminator), self._age))
        return categoriser

    def observational_transmit(self, game_dict):
        '''Speaker uses this to transmit form to hearer in the observational game.'''
        meaning = self._get_neighborhood(self.pos)
        interpretation = self.memory.get_meaning(game_dict['form'])
        game_dict['hearer_meaning'] = meaning
        game_dict['hearer_interpretation'] = interpretation
        self.memory.strengthen_form(meaning, game_dict['form'], speaker=False)
        self.stat_dict['memories'].append((copy.deepcopy(self.memory), self._age))
        self.model.report_place_game(game_dict)

    def guessing_transmit(self, disc_form):
        '''Speaker uses this to transmit form to hearer in the guessing game.'''
        if self._last_broadcast is None or self._last_broadcast['categoriser'] is None:
            return False
        current_place = self._get_neighborhood(self.pos)
        if current_place != self._last_broadcast['place']:
            return False
        if self.pos not in self._last_broadcast['topic_objects']:
            return False
        categoriser = self._last_broadcast['categoriser']
        self.memory.strengthen_form(categoriser, disc_form, speaker=False)
        if self._gather_stats:
            self.stat_dict['memories'].append((copy.deepcopy(self.memory), self._age))
        return True

    def _play_guessing_game(self, place, hearer):
        '''Start the guessing game as the speaker.'''
        if self._premade_lang:
            return
        if self._last_broadcast is None:
            return
        if self._last_broadcast['place'] != place:
            return
        if self.pos not in self._last_broadcast['topic_objects']:
            return
        categoriser = self._last_broadcast['categoriser']
        self.stat_dict['guessing_game_init'] += 1
        form = self._last_broadcast['disc_form']
        if hearer.guessing_transmit(form):
            self.memory.strengthen_form(categoriser, form, speaker=True)
            if self._gather_stats:
                self.stat_dict['memories'].append((copy.deepcopy(self.memory), self._age))

    def _play_observational_game(self, hearer):
        '''Start the observational game as the speaker.'''
        self.stat_dict['obs_game_init'] += 1
        meaning = self._get_neighborhood(self.pos)
        form = self.memory.get_form(meaning)
        if form is None:
            form = self.memory.invent_form()
            self.memory.create_association(meaning, form)
        self.memory.report_form_use(meaning, form)
        self.memory.strengthen_form(meaning, form, speaker=True)
        if self._gather_stats:
            self.stat_dict['memories'].append((copy.deepcopy(self.memory), self._age))
        hearer.observational_transmit({'form': form, 'speaker_meaning': meaning})
        if self._guessing_game:
            self._play_guessing_game(meaning, hearer)
        return meaning

    def _reroute(self):
        '''Finds a new route to destination assuming that the first step in the current route is blocked.'''
        neighborhood = self.model.grid.get_neighbors(self.pos, False)
        env_map = np.copy(self.map)
        for neighbor in neighborhood:
            x, y = neighbor.pos
            env_map[x][y] = 1
        if self._blocked is not None:
            env_map[self._blocked] = 1
        new_path = astar(env_map, self.pos, self._destination, False)[1:]
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

    def _calculate_path(self, map):
        return astar(map, self.pos, self._destination, False)[1:]

    def ask_if_free(self, place_form, disc_form):
        '''Used to ask an agent if a place is free. Returns the answer and interpreted place and categoriser.'''
        place = self.memory.get_meaning(place_form)
        if place is None:
            return True, None, None
        categoriser = self.memory.get_meaning(disc_form)
        if categoriser is None:
            return True, place, None
        objects = self._get_objects(place)
        normalised = self._normalise(objects)
        low, high = categoriser.range
        for obj in zip(objects, normalised):
            if low <= obj[1][categoriser.channel] <= high:
                if obj[0] == self.pos or obj[0] in self._path:
                    return False, place, categoriser
        return True, place, categoriser

    def _get_forms_for_path(self, path, path2):
        '''Returns forms for meanings used to discriminate path from path2 (and other things)..'''
        place = self._get_highest_meaning_on_path(path)
        # place = (('S', 'S', 'S'), ('.', 'X', '.'), ('S', 'S', 'S'))
        if place is None:
            return None, None, None, None, None
        place_form = self.memory.get_form(place)
        objects = self._get_objects(place)
        normalised = self._normalise(objects)
        topic_objects_normal = set([obj[1] for obj in zip(objects, normalised) if obj[0] in path])
        path2_objects_normal = set([obj[1] for obj in zip(objects, normalised) if obj[0] in path2])

        if len(path2_objects_normal) == 0 or len(topic_objects_normal & path2_objects_normal) > 0:
            return None, None, None, None, None

        # Find a categoriser that can discriminate between the options
        categoriser = self._discriminate(normalised, topic_objects_normal, path2_objects_normal)
        if categoriser is not None:
            disc_form = self.memory.get_form(categoriser)
            if disc_form is None:
                disc_form = self.memory.invent_form()
                self.memory.create_association(categoriser, disc_form)
        else:
            disc_form = None
        topic_objects = [obj for obj in objects if obj in path]
        return place, place_form, categoriser, disc_form, topic_objects

    def _get_options(self):
        option1 = self._calculate_path(self.model.map)
        map = np.copy(self.model.map)
        map[option1[-2]] = 1
        option2 = self._calculate_path(map)
        return option1, option2

    def _broadcast_question(self):
        '''Considers two shortest paths to the destination and returns the one that is okay with other agents.'''
        # self.map = np.copy(self.model.map)
        option1, option2 = self._get_options()

        if len(option2) == 0:
            self._blocked = None
            self._last_broadcast = None
            # Only one option
            return option1

        if not self._guessing_game:
            if self._rand_behaviour:
                if np.random.random() < 0.5:
                    self._blocked = option2[-2]
                    return option1
                else:
                    self._blocked = option1[-2]
                    return option2
            else:
                self._blocked = option2[-2]
                return option1

        broadcast1, broadcast2 = None, None

        # First ask if option1 is free
        place, place_form, categoriser, disc_form, topic_objects = self._get_forms_for_path(option1, option2)

        # if place != (('S', 'S', 'S'), ('.', 'X', '.'), ('S', 'S', 'S')):
        #     return option1

        if not (place is None or place_form is None or categoriser is None or disc_form is None):
            self.memory.report_form_use(categoriser, disc_form)
            broadcast1 = {'place': place,
                          'place_form': place_form,
                          'categoriser': categoriser,
                          'disc_form': disc_form,
                          'topic_objects': topic_objects}
            if self.model.broadcast_question(place, place_form, categoriser, disc_form, self):
                self.stat_dict['option1_selected'] += 1
                self._blocked = option2[-2]
                self._last_broadcast = broadcast1
                return option1

        # If option1 wasn't free, check option2
        place, place_form, categoriser, disc_form, topic_objects = self._get_forms_for_path(option2, option1)
        if not (place is None or place_form is None or categoriser is None or disc_form is None):
            self.memory.report_form_use(categoriser, disc_form)
            broadcast2 = {'place': place,
                          'place_form': place_form,
                          'categoriser': categoriser,
                          'disc_form': disc_form,
                          'topic_objects': topic_objects}
            if self.model.broadcast_question(place, place_form, categoriser, disc_form, self):
                self.stat_dict['extra_distance'] += len(option2) - len(option1)
                self.stat_dict['option2_selected'] += 1
                self._blocked = option1[-2]
                self._last_broadcast = broadcast2
                return option2

        # Random selection
        if np.random.random() < 0.5:
            self.stat_dict['option1_selected'] += 1
            self._blocked = option2[-2]
            self._last_broadcast = broadcast1
            return option1

        self.stat_dict['option2_selected'] += 1
        self._blocked = option1[-2]
        self._last_broadcast = broadcast2
        return option2

        # If no path was free, use option1
        # self._last_broadcast = None
        # self.stat_dict['option1_selected'] += 1
        # self._blocked = option2[-2]
        # return option1

    def step(self):
        self._age += 1
        self.map = np.copy(self.model.map)
        if self._path is None or len(self._path) == 0:
            self._path = self._calculate_path(self.map)

    def finish_step(self):
        # Reached destination
        if len(self._path) < 2 and len(self._path) > 0:
            x, y = self._destination
            if type(self.model.grid[x][y]) is ActionCenter:
                ac = self.model.grid[x][y]
                self._destination = ac.get_mission()
                if self._has_item:
                    self.stat_dict['items_delivered'] += 1
                    self.stat_dict['delivery_times'].append(self._age - self._last_delivery)
                    self._last_delivery = self._age
                self._has_item = False
                self._path = self._broadcast_question()
            else:
                self._destination = self.model.action_center.pos
                self._has_item = True
                self._path = self._calculate_path(self.map)


SYMBOLS = {
    # AgentBasic: 'A',
    AgentBasic: '.',
    Wall: 'W',
    Shelf: 'S',
    ActionCenter: 'C',
    type(None): '.',
    'self': 'X'
}
