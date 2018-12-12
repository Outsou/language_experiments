import random


class Categoriser:
    def __init__(self, range, channel, parent=None):
        self.parent = parent
        self.range = range
        self.channel = channel
        self.child1 = None
        self.child2 = None
        self.use_count = 0
        self.success_count = 0
        self.age = 0

    def split(self):
        middle = (self.range[0] + self.range[1]) / 2
        range1 = (self.range[0], middle)
        range2 = (middle, self.range[1])
        child1 = Categoriser(range1, self.channel, self)
        child2 = Categoriser(range2, self.channel, self)
        return child1, child2

    def grow(self):
        if self.child1 is not None or self.child2 is not None:
            return
        child1, child2 = self.split()
        self.child1 = child1
        self.child2 = child2

    def prune(self):
        if self.parent.child1 == self:
            self.parent.child1 = None
        else:
            self.parent.child2 = None

    def discriminate(self, value):
        if self.child1 is not None and self.child1.range[0] <= value <= self.child1.range[1]:
            return self.child1.discriminate(value)
        elif self.child2 is not None and self.child2.range[0] <= value <= self.child2.range[1]:
            return self.child2.discriminate(value)
        return self

    def _get_new_values(self, node, values):
        new_values = set()
        for val in values:
            if node.range[0] <= val <= node.range[1]:
                new_values.add(val)
        return new_values

    def __hash__(self):
        return int(str(self.range.__hash__()) + str(self.channel.__hash__()))

    def __eq__(self, other):
        return type(other) == Categoriser and self.range == other.range and self.channel == other.channel

    # def set_discriminate(self, value, all_values):
    #     if self.child1 is not None and self.child1.range[0] <= value <= self.child1.range[1]:
    #         new_values = self._get_new_values(self.child1, all_values)
    #         if len(new_values) < all_values:
    #             return self.child1.set_discriminate(value, new_values)
    #     if self.child2 is not None and self.child2.range[0] <= value <= self.child2.range[1]:
    #         new_values = self._get_new_values(self.child1, all_values)
    #         if len(new_values) < all_values:
    #             return self.child1.set_discriminate(value, new_values)
    #     return self

    def set_discriminate(self, topic_vals, previous_set, best_discriminator):
        if self.child1 is not None:
            new_set = self._get_new_values(self.child1, previous_set)
            if topic_vals <= new_set:
                if len(new_set) < len(previous_set):
                    best_discriminator = self.child1
                return self.child1.set_discriminate(topic_vals, new_set, best_discriminator)
        if self.child2 is not None:
            new_set = self._get_new_values(self.child2, previous_set)
            if topic_vals <= new_set:
                if len(new_set) < len(previous_set):
                    best_discriminator = self.child2
                return self.child2.set_discriminate(topic_vals, new_set, best_discriminator)
        return best_discriminator

class DiscriminationTree:
    def __init__(self, range, channel):
        self.root = Categoriser(range, channel)

    def increase_age(self):
        def _increase(categoriser):
            if categoriser.child1 is not None:
                _increase(categoriser.child1)
            if categoriser.child2 is not None:
                _increase(categoriser.child2)
            categoriser.age += 1
        _increase(self.root)

    def discriminate(self, value):
        '''Returns the lowest node (discriminator) in the tree that contains the value.'''
        return self.root.discriminate(value)

    def set_discriminate(self, all_vals, topic_vals):
        return self.root.set_discriminate(topic_vals, all_vals, None)

    def grow(self):
        random.choice(self.get_leaves()).grow()

    def get_leaves(self):
        '''Returns the leaves of the tree.'''
        nodes = [self.root]
        leaves = []
        while len(nodes) > 0:
            new_nodes = []
            for node in nodes:
                if node.child1 is None and node.child2 is None:
                    leaves.append(node)
                if node.child1 is not None:
                    new_nodes.append(node.child1)
                if node.child2 is not None:
                    new_nodes.append(node.child2)
            nodes = new_nodes
        return leaves

class Discriminator:
    def __init__(self, ranges):
        self.trees = []
        for i in range(len(ranges)):
            self.trees.append(DiscriminationTree(ranges[i], i))

    def discriminate(self, all_objects, topic_objects):
        '''Returns the categoriser that perfectly discriminates topic objects from all objects.'''
        topic_set = set(topic_objects)
        for i in range(len(self.trees)):
            discrimination_dict = {}
            for obj in all_objects:
                categoriser = self.trees[i].discriminate(obj[i])
                if categoriser not in discrimination_dict:
                    discrimination_dict[categoriser] = set()
                discrimination_dict[categoriser].add(obj)
            for categoriser, objs in discrimination_dict.items():
                if objs == topic_set:
                    return categoriser
        # Discrimination failed :(
        return None

    def set_discriminate(self, all_objects, topic_objects, disc_objects):
        '''Finds the lowest categoriser in a tree that adds accuracy to the discrimination. Then checks if it
        discriminates topic_objects from disc_objects.'''
        for i in range(len(self.trees)):
            topic_vals = set([obj[i] for obj in topic_objects])
            all_vals = set([obj[i] for obj in all_objects])
            categoriser = self.trees[i].set_discriminate(all_vals, topic_vals)
            if categoriser is not None:
                other_disc = [obj for obj in disc_objects if categoriser.range[0] <= obj[i] <= categoriser.range[1]]
                if len(other_disc) == 0:
                    return categoriser
        return None

    def _gather_leaves(self):
        leaves = []
        for tree in self.trees:
            leaves += tree.get_leaves()
        return leaves

    def _grow_a_leaf(self, all_objects, topic_objects):
        '''Finds and grows a leaf, whose possible children can discriminate topic objects from all objects.
        If no such leaf is found, a random leaf is grown.'''
        topic_objects = set(topic_objects)
        leaves = self._gather_leaves()
        random.shuffle(leaves)
        for leaf in leaves:
            chan = leaf.channel
            child1, child2 = leaf.split()
            for categoriser in [child1, child2]:
                objects = set()
                for obj in all_objects:
                    if categoriser.range[0] <= obj[chan] <= categoriser.range[1]:
                        objects.add(obj)
                if objects == topic_objects:
                    if leaf.channel == 1 and (leaf.range == (0, 0.5) or leaf.range == (0.5, 1)):
                        print('what')
                    leaf.child1 = child1
                    leaf.child2 = child2
                    return
        # TODO: Check if the objects can be discriminated
        leaves[0].grow()

    def grow(self, channel=None, disc_objects=None, topic_objects=None):
        '''Randomly selects a channel to grow.'''
        all_objects = set(disc_objects) | set(topic_objects)

        if channel is None and all_objects is None and topic_objects is None:
            leaves = self._gather_leaves()
            random.choice(leaves).grow()
        elif channel is not None and all_objects is None and topic_objects is None:
            self.trees[channel].grow()
        else:
            self._grow_a_leaf(all_objects, topic_objects)