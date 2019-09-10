from utils.str2notes import str2notes
from .note import Note

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

class Rule(object):
    ONCE = 'once'
    EVERYTIME = 'everytime'

    def __init__(self, notes, trigger, attributes):
        self.set(notes, trigger, attributes)

    def set(self, notes, trigger, attributes):
        if type(notes) is str:
            self.notes = set(str2notes(notes))
        elif type(notes) is set:
            self.notes = set(Note(note) if type(note) is not Note else note for note in notes)

        self.trigger = trigger
        self.attributes = Rule.ONCE if attributes == 'once' else Rule.EVERYTIME

    def __repr__(self):
        return f'Rule(notes={self.notes}, trigger={self.trigger}, attributes={self.attributes})'

    def match(self, context):
        return self.notes.issubset(context.notes)


class RuleSet(object):
    def __init__(self, name):
        self.name = name
        self.rules = []

    def add(self, rule):
        self.rules.append(rule)

    def examine(self, context):
        for rule in self.rules:
            match = rule.match(context)

            if match:
                print(f'> {rule.trigger}')

    def __repr__(self):
        return f'RuleSet({self.name})'
