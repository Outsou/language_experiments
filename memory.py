import random
import operator


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


class MFAssociationMemory:
    def __init__(self):
        self.mf_dict = {}
        self.meaning_stats = {}
        self.increment = 0.1
        self.min = 0
        self.max = 1
        self.known_forms = set()
        self.a = 0.1

    def _update_utility(self, meaning, utility):
        old_util = self.meaning_stats[meaning]['utility']
        self.meaning_stats[meaning]['utility'] = (1 - self.a) * old_util + self.a * utility

    def create_association(self, meaning, form):
        if meaning not in self.mf_dict:
            self.mf_dict[meaning] = {form: self.increment}
            self.meaning_stats[meaning] = {'utility': 0.0, 'speaker': 0, 'listener': 0}
        elif form not in self.mf_dict[meaning]:
            self.mf_dict[meaning][form] = self.min
        self.known_forms.add(form)

    def strengthen_form(self, meaning, form, utility):
        for associated_form in self.mf_dict[meaning].keys():
            if associated_form and associated_form != form:
                self.mf_dict[meaning][associated_form] = max(
                    self.min,
                    round(self.mf_dict[meaning][associated_form] - self.increment, 1))
        self.mf_dict[meaning][form] = min(
            self.max,
            round(self.mf_dict[meaning][form] + self.increment, 1))
        self._update_utility(meaning, utility)
        self.meaning_stats[meaning]['speaker'] += 1

    def strengthen_meaning(self, meaning, form, utility):
        for associated_meaning in self.mf_dict.keys():
            if associated_meaning != meaning and form in self.mf_dict[associated_meaning]:
                self.mf_dict[associated_meaning][form] = max(
                    self.min,
                    round(self.mf_dict[associated_meaning][form] - self.increment, 1))
        if meaning not in self.mf_dict:
            self.mf_dict[meaning] = {}
            self.meaning_stats[meaning] = {'utility': 0.0, 'speaker': 0, 'listener': 0}
        if form not in self.mf_dict[meaning]:
            self.mf_dict[meaning][form] = self.min
        self.mf_dict[meaning][form] = min(
            self.max,
            round(self.mf_dict[meaning][form] + self.increment, 1))
        self._update_utility(meaning, utility)
        self.meaning_stats[meaning]['listener'] += 1

    def weaken_association(self, meaning, form):
        self.mf_dict[meaning][form] = max(
            self.min,
            round(self.mf_dict[meaning][form] - self.increment, 1))

    def invent_form(self):
        def create_form(length):
            vowels = ['A', 'E', 'I', 'O', 'U', 'Y']
            consonants = ['B', 'C', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M',
                          'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'X', 'Z']
            form = ''
            for _ in range(length):
                form += random.choice(consonants)
                form += random.choice(vowels)
            return form

        length = random.choice(range(3)) + 1
        form = create_form(length)
        while form in self.known_forms:
            form = create_form(length)
        return form

    def get_form(self, meaning):
        if meaning not in self.mf_dict:
            return None
        forms = [x for x in self.mf_dict[meaning].items() if x[0] != 'utility']
        form, score = max(forms, key=operator.itemgetter(1))
        return form if score > 0 else None

    def get_meaning(self, form):
        strongest = None
        score = -1
        for meaning, forms in self.mf_dict.items():
            if form in forms:
                if forms[form] > score:
                    score = forms[form]
                    strongest = meaning
        return strongest if score > 0 else None
