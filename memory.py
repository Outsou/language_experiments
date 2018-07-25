class ExplicitMemory:
    def __init__(self):
        self.max_consequences = 5
        self.mem = {}
        self.word_associations = {}

    def add_memory(self, concept, consequence):
        if concept not in self.mem:
            self.mem[concept] = []
        self.mem[concept].append(consequence)
        if len(self.mem[concept]) > self.max_consequences:
            del self.mem[concept][0]

    def invoke_memory(self, concept):
        if concept not in self.mem:
            return None
        return sum(self.mem[concept]) / len(self.mem[concept])

    def associate_word(self, concept, word):
        self.word_associations[concept] = word

    def get_word(self, state):
        if state not in self.word_associations:
            return None
        return self.word_associations[state]

    def get_all_words(self):
        return self.word_associations.keys()
