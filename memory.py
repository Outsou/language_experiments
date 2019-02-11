import random
import operator
import copy


class MFAssociationMemory:
    def __init__(self):
        self.mf_dict = {}
        self.meaning_stats = {}
        self.stat_start_vals = {'utility': None, 'speaker': 0, 'listener': 0, 'use_counts': {}}
        self.increment = 0.1
        self.min = 0
        self.max = 1
        self.known_forms = set()
        self.a = 0.1

    def _update_utility(self, meaning, utility):
        old_util = self.meaning_stats[meaning]['utility']
        if old_util is None:
            self.meaning_stats[meaning]['utility'] = utility
        else:
            self.meaning_stats[meaning]['utility'] = (1 - self.a) * old_util + self.a * utility

    def report_form_use(self, meaning, form):
        assert meaning in self.meaning_stats
        if form not in self.meaning_stats[meaning]['use_counts']:
            self.meaning_stats[meaning]['use_counts'][form] = 0
        self.meaning_stats[meaning]['use_counts'][form] += 1

    def create_association(self, meaning, form):
        if meaning not in self.mf_dict:
            self.mf_dict[meaning] = {form: self.increment}
            self.meaning_stats[meaning] = copy.deepcopy(self.stat_start_vals)
        elif form not in self.mf_dict[meaning]:
            self.mf_dict[meaning][form] = self.min
        self.known_forms.add(form)

    def strengthen_form(self, meaning, form, speaker=None, utility=None):
        if meaning not in self.mf_dict:
            self.mf_dict[meaning] = {}
            self.meaning_stats[meaning] = copy.deepcopy(self.stat_start_vals)
        if form not in self.mf_dict[meaning]:
            self.mf_dict[meaning][form] = self.min
        for associated_form in self.mf_dict[meaning].keys():
            if associated_form and associated_form != form:
                self.mf_dict[meaning][associated_form] = max(
                    self.min,
                    round(self.mf_dict[meaning][associated_form] - self.increment, 1))
        self.mf_dict[meaning][form] = min(
            self.max,
            round(self.mf_dict[meaning][form] + self.increment, 1))
        if utility is not None:
            self._update_utility(meaning, utility)
        for associated_meaning in self.mf_dict.keys():
            if associated_meaning != meaning and form in self.mf_dict[associated_meaning]:
                self.mf_dict[associated_meaning][form] = max(
                    self.min,
                    round(self.mf_dict[associated_meaning][form] - self.increment, 1))
        if speaker is not None:
            if speaker:
                self.meaning_stats[meaning]['speaker'] += 1
            else:
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

        length = 4
        form = create_form(length)
        while form in self.known_forms:
            form = create_form(length)
        return form

    def get_form(self, meaning):
        if meaning not in self.mf_dict:
            return None
        max_forms = []
        max_score = -1
        for form, score in self.mf_dict[meaning].items():
            if score > max_score:
                max_forms = []
                max_score = score
            if score == max_score:
                max_forms.append(form)
        # forms = [x for x in self.mf_dict[meaning].items()]
        # form, score = max(forms, key=operator.itemgetter(1))
        return None if len(max_forms) == 0 else random.choice(max_forms)

    def get_highest_score(self, meaning):
        max_score = 0.0
        if meaning not in self.mf_dict:
            return max_score
        for form, score in self.mf_dict[meaning].items():
            if score > max_score:
                max_score = score
        return max_score

    def get_meaning(self, form):
        strongest = None
        score = 0
        for meaning, forms in self.mf_dict.items():
            if form in forms:
                if forms[form] > score:
                    score = forms[form]
                    strongest = meaning
        return strongest

    def get_utility(self, meaning):
        return None if meaning not in self.meaning_stats else self.meaning_stats[meaning]['utility']

    def make_form_known(self, form):
        self.known_forms.add(form)

    def is_associated(self, meaning, form):
        if meaning not in self.mf_dict or form not in self.mf_dict[meaning]:
            return False
        return True
