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

    def grow(self):
        if self.child1 is not None or self.child2 is not None:
            return
        middle = int(self.range[1] / 2)
        range1 = (self.range[0], middle)
        range2 = (middle + 1, self.range[1])
        self.child1 = Categoriser(range1, self.channel, self)
        self.child2 = Categoriser(range2, self.channel, self)

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
        return self.root.discriminate(value)

    def grow(self):
        self.root.grow()

class Discriminator:
    def __init__(self, ranges):
        self.trees = []
        for i in range(len(ranges)):
            self.trees.append(DiscriminationTree(ranges[i], i))

    def discriminate(self, all_objects, topic_objects):
        '''Returns the discriminator that perfectly discriminates topic objects from all objects.'''
        topic_set = set(topic_objects)
        for i in range(len(self.trees)):
            discrimination_dict = {}
            for obj in all_objects:
                discriminator = self.trees[i].discriminate(obj[i])
                if discriminator not in discrimination_dict:
                    discrimination_dict[discriminator] = set()
                discrimination_dict[discriminator].add(obj)
            for discriminator, objs in discrimination_dict.items():
                if objs == topic_set:
                    return discriminator
        # Discrimination failed :(
        return None

    def get_relevant_discriminators(self, disc_obj, all_objs):
        '''Returns all discriminators that somehow discriminate the disc_obj from other objects.'''
        relevant_discriminators = []
        for i in range(len(self.trees)):
            discriminators = {}
            relevant_discriminator = None
            for obj in all_objs:
                discriminator = self.trees[i].discriminate(obj[i])
                if discriminator not in discriminators:
                    discriminators[discriminator] = []
                discriminators[discriminator].append(obj)
                if obj == disc_obj:
                    relevant_discriminator = discriminator
            if len(discriminators.keys()) > 1:
                relevant_discriminators.append(relevant_discriminator)
        return relevant_discriminators

    def grow(self):
        '''Randomly selects a channel to grow.'''
        random.choice(self.trees).grow()