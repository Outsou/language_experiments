class Categoriser:
    def __init__(self, range, parent=None):
        self.parent = parent
        self.range = range
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
        self.child1 = Categoriser(range1, self)
        self.child2 = Categoriser(range2, self)

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
    def __init__(self, range):
        self.root = Categoriser(range, None)

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
