import random
import math


class Categoriser:
    def __init__(self, range, channel, parent=None):
        self.parent = parent
        self.range = range
        self.channel = channel
        self.child1 = None
        self.child2 = None
        self.age = 0
        self.applicability_count = 0
        self.form_associations = {}

    def grow(self):
        if self.child1 is not None or self.child2 is not None:
            return
        middle = self.range[1] / 2
        range1 = (self.range[0], middle)
        range2 = (middle, self.range[1])
        self.child1 = Categoriser(range1, self.channel, self)
        self.child2 = Categoriser(range2, self.channel, self)

    def prune(self):
        if self.parent.child1 == self:
            self.parent.child1 = None
        else:
            self.parent.child2 = None

    def discriminate(self, value, form):
        self.applicability_count += 1
        if form not in self.form_associations:
            self.form_associations[form] = 0
        self.form_associations[form] += 1

        if self.child1 is not None and self.child1.range[0] <= value <= self.child1.range[1]:
            return self.child1.discriminate(value, form)
        elif self.child2 is not None and self.child2.range[0] <= value <= self.child2.range[1]:
            return self.child2.discriminate(value, form)
        return self

class DiscriminationTree:
    def __init__(self, channel, range=(0, 1), e=0.05, evidence_threshold=5):
        self.root = Categoriser(range, channel)
        self.e = e
        self.et = evidence_threshold

    def increase_age(self):
        def _increase(categoriser):
            if categoriser.child1 is not None:
                _increase(categoriser.child1)
            if categoriser.child2 is not None:
                _increase(categoriser.child2)
            categoriser.age += 1
        _increase(self.root)

    def discriminate(self, value, form):
        '''Returns the lowest node (discriminator) in the tree that contains the value.'''
        return self.root.discriminate(value, form)

    def grow(self):
        self.root.grow()

    def get_next_category(self, form, category):
        if category.child1 is None or category.child2 is None:
            return None, None
        if category.child1.applicability_count < self.et or category.child2.applicability_count < self.et:
            return None, None

        if form not in category.child1.form_associations or category.child1.applicability_count == 0:
            child1_p = 0
        else:
            child1_p = category.child1.form_associations[form] / category.child1.applicability_count

        if form not in category.child2.form_associations or category.child2.applicability_count == 0:
            child2_p = 0
        else:
            child2_p = category.child2.form_associations[form] / category.child2.applicability_count

        if child1_p == 0 and child2_p == 0:
            return None, None

        own_p = category.form_associations[form] / category.applicability_count
        last_category = category
        if abs(child1_p - child2_p) < self.e:
            return None, None
        if child1_p - own_p > self.e:
            category = category.child1
        elif child2_p - own_p > self.e:
            category = category.child2
        if last_category == category:
            return None, None
        return category, abs(child1_p - child2_p)

    def get_best_category(self, form):
        category, _ = self.get_next_category(form, self.root)
        next_category = category
        while next_category is not None:
            category = next_category
            next_category, _ = self.get_next_category(form, category)
        return category

class Discriminator:
    def __init__(self, channels, ranges=None):
        self.trees = []
        if ranges is not None:
            assert channels == len(ranges), 'Channels and the amount of given ranges does not match.'
            for i in range(len(channels)):
                self.trees.append(DiscriminationTree(i, ranges[i]))
        else:
            for i in range(channels):
                self.trees.append(DiscriminationTree(i))

    def discriminate_object(self, obj, form):
        for i in range(len(self.trees)):
            self.trees[i].discriminate(obj[i], form)

    def get_best_category(self, form):
        best_chan = 0
        best_diff = -1
        for i in range(len(self.trees)):
            cat, diff = self.trees[i].get_next_category(form, self.trees[i].root)
            if cat is not None:
                if diff > best_diff:
                    best_diff = diff
                    best_chan = i
        return self.trees[best_chan].get_best_category(form), best_diff

    def grow(self, set1=None, set2=None):
        '''Randomly selects a channel to grow.'''
        random.choice(self.trees).grow()

def normalize(objs):
    chan_vals = list(zip(*objs))
    normalized_vals = []
    for chan in chan_vals:
        min_val =min(chan)
        max_val = max(chan)
        length = max_val - min_val
        normalized_vals.append(tuple((val - min_val) / length for val in chan))
    return list(zip(*normalized_vals))

def get_nodes(val, tree):
    nodes = []
    node = tree.root
    while node is not None:
        if node.child1 is not None and node.child1.range[0] <= val <= node.child1.range[1]:
            nodes.append(node.child1)
            node = node.child1
        elif node.child2 is not None and node.child2.range[0] <= val <= node.child2.range[1]:
            nodes.append(node.child2)
            node = node.child2
        else:
            node = None
    return nodes

def name_nodes(discriminator):
    name = 0
    names = {}
    for tree in discriminator.trees:
        nodes = [tree.root]
        while len(nodes) > 0:
            next_nodes = []
            for node in nodes:
                name += 1
                names[node] = name
                if node.child1 is not None:
                    next_nodes.append(node.child1)
                if node.child2 is not None:
                    next_nodes.append(node.child2)
            nodes = next_nodes
    return names

def print_tree(tree):
    nodes = [tree.root]
    while len(nodes) > 0:
        new_nodes = []
        for node in nodes:
            print(node.range)
            for form, count in node.form_associations.items():
                print('{}: {}'.format(form, count / node.applicability_count))
            print()
            if node.child1 is not None:
                new_nodes.append(node.child1)
            if node.child2 is not None:
                new_nodes.append(node.child2)
        nodes = new_nodes

def print_range_forms(tree, forms):
    nodes = [tree.root]
    while len(nodes) > 0:
        new_nodes = []
        for node in nodes:
            print('{}: {}'.format(node.range, forms[node]))
            if node.child1 is not None:
                new_nodes.append(node.child1)
            if node.child2 is not None:
                new_nodes.append(node.child2)
        nodes = new_nodes

def find_form(discriminator, forms, categoriser):
    options = []
    for form in forms:
        cat, diff = discriminator.get_best_category(form)
        if cat == categoriser:
            options.append((cat, diff))
    if len(options) == 0:
        return None
    from operator import itemgetter
    return max(options, key=itemgetter(1))[0]

def add_new_form(form, categoriser):
    categoriser.form_associations[form] = 1
    categoriser.applicability_count += 1
    next_cat = categoriser.parent
    while next_cat is not None:
        cat = next_cat
        cat.form_associations[form] = 1
        cat.applicability_count += 1
        next_cat = cat.parent

if __name__ == '__main__':
    runs = 1000
    iters = 1500
    success = [0] * iters
    for j in range(runs):
        print('run {}'.format(j))
        discriminator1 = Discriminator(2)
        discriminator1.trees[0].grow()
        discriminator1.trees[0].root.child1.grow()
        discriminator1.trees[0].root.child2.grow()
        discriminator1.trees[1].grow()
        invented1 = {}

        discriminator2 = Discriminator(2)
        discriminator2.trees[0].grow()
        discriminator2.trees[0].root.child1.grow()
        discriminator2.trees[0].root.child2.grow()
        discriminator2.trees[1].grow()
        invented2 = {}

        forms = set()

        objs1 = [(2, y) for y in range(1, 8)]
        objs1 += [(4, y) for y in range(1, 8)]
        objs1 += [(6, y) for y in range(1, 8)]
        objs1 += [(8, y) for y in range(1, 8)]
        objs1 = normalize(objs1)

        objs2 = [(x, 11) for x in range(11, 18)]
        objs2 += [(x, 13) for x in range(11, 18)]
        objs2 = normalize(objs2)

        objs1_prob = len(objs1) / (len(objs1) + len(objs2))

        i = 0
        guesses = []
        while i < iters:
            i += 1
            if random.random() < 0.5:
                speaker = discriminator1
                hearer = discriminator2
                invented = invented1
            else:
                speaker = discriminator2
                hearer = discriminator1
                invented = invented2

            # speaker = discriminator1
            # hearer = discriminator2

            if random.random() < objs1_prob:
                objs = objs1
                obj = random.choice(objs)
                categoriser = random.choice(get_nodes(obj[0], speaker.trees[0]))
            else:
                objs = objs2
                obj = random.choice(objs)
                categoriser = random.choice(get_nodes(obj[1], speaker.trees[1]))

            # SPEAKER
            form = find_form(speaker, forms, categoriser)
            if form is None:
                if categoriser in invented:
                    form = invented[categoriser]
                else:
                    form = len(forms) + 1
                    forms.add(form)
                    invented[categoriser] = form
                # add_new_form(form, categoriser)

            # asd = speaker.get_best_category(form)

            # HEARER
            hearer.discriminate_object(obj, form)
            guess, _ = hearer.get_best_category(form)
            if guess is not None:
                guesses.append(guess.range == categoriser.range)
            else:
                guesses.append(False)

        for k in range(len(guesses)):
            if guesses[k]:
                success[k] += 1
        print(len(forms))

    success_ratios = [x / runs for x in success]
    print(success_ratios)
    import matplotlib.pyplot as plt

    plt.plot(success_ratios)
    plt.show()
    asd = 1
