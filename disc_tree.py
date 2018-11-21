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
        # TODO: Return the lowest node that adds accuracy
        return self.root.discriminate(value)

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
                    leaf.child1 = child1
                    leaf.child2 = child2
                    return
        # TODO: Check if the objects can be discriminated
        # leaves[0].grow()

    def grow(self, channel=None, all_objects=None, topic_objects=None):
        '''Randomly selects a channel to grow.'''
        if channel is None and all_objects is None and topic_objects is None:
            leaves = self._gather_leaves()
            random.choice(leaves).grow()
        elif channel is not None and all_objects is None and topic_objects is None:
            self.trees[channel].grow()
        else:
            self._grow_a_leaf(all_objects, topic_objects)