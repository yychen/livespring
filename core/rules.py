from enum import Enum

from utils.str2notes import str2notes
from .note import Note

import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

import os


class RuleType(Enum):
    ONCE = 'once'
    EVERYTIME = 'everytime'


class Rule(object):
    def __init__(self, name, notes, trigger, rule_type, enabled=True):
        self.set(name, notes, trigger, rule_type, enabled)

    def set(self, name, notes, trigger, rule_type, enabled=True):
        self.name = name

        if type(notes) is str:
            self.notes = set(str2notes(notes))
        elif type(notes) is set:
            self.notes = set(Note(note) if type(note) is not Note else note for note in notes)

        self.trigger = trigger
        self.type = RuleType(rule_type)
        self.enabled = enabled

    def __repr__(self):
        return f'Rule(notes={self.notes}, trigger={self.trigger}, type={self.type}, enabled={self.enabled})'

    def __str__(self):
        return self.name

    def match(self, context):
        return self.notes.issubset(context.notes)

    @classmethod
    def loads(cls, data, name_prefix=None, order=None):
        # Deserialize data and return a rule instance

        # Deal with the name
        name = data.get('name', None)

        if not name and order is not None:
            name = f'#{order}'

        if not name:
            name = 'undefined'

        if name_prefix:
            name = f'{name_prefix}.{name}'

        # Make the rule
        r = Rule(name, data.get('notes'), data.get('trigger'), data.get('type'), data.get('enabled'))
        return r

    # TODO: serializing the name should be a problem. Needs refactoring here
    # Maybe split "name" and "display"
    # Need a way to store the original data that was loaded
    def dumps(self):
        out = {
            'name': self.name,
            'notes': ' '.join(str(note) for note in sorted(self.notes)),
            'trigger': self.trigger,
            'type': self.type.value,
            'enabled': self.enabled,
        }

        return out


class RuleSet(object):
    def __init__(self, name):
        self.name = name
        self.rules = []

    def add(self, rule):
        self.rules.append(rule)

    def examine(self, context):
        triggered = []
        for rule in self.rules:
            match = rule.match(context)

            if match:
                print(f'> {rule.trigger}')
                triggered.append(rule.trigger)

        return triggered

    def __repr__(self):
        return f'RuleSet({self.name})'

    @classmethod
    def load(cls, path):
        rs = None

        # Loads the yaml file
        with open(path, 'r') as f:
            rs = cls(os.path.basename(path))
            document = yaml.load(f, Loader=Loader)

            if type(document) is not list:
                raise ValueError(f'{path} is not valid yaml file')

            for index, entry in enumerate(document):
                rule = Rule.loads(entry, name_prefix=rs.name, order=index)
                rs.add(rule)
                print(f'Rule {rule.name} loaded: {repr(rule)}')
                # print(rule.dumps())

        return rs
