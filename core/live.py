from .context import Context
from .rules import Rule, RuleSet
from .note import Note

from collections import OrderedDict

class Live(object):
    class RuleSets(object):
        def __init__(self, parent):
            self.sets = OrderedDict()
            self.current = None
            self.parent = parent

        def load(self, rule_sets):
            for rule_set in rule_sets:
                self.add(rule_set)

        def add(self, rule_set, current=False):
            if not isinstance(rule_set, RuleSet):
                raise TypeError(f'{rule_set} is not a RuleSet')

            self.sets[rule_set.name] = rule_set
            if current:
                self.set_current(rule_set.name)

        def set_current(self, name):
            if not name:
                # Set current to None
                self.current = None
            else:
                try:
                    self.current = self.sets[name]
                except KeyError:
                    print(f'Cannot find rule set {name}, not changing anything...')
                    return

            print(f'Setting current rule set to {name}')
            self.parent.send_status()

        def set_default(self):
            if self.sets:
                self.set_current(next(iter(self.sets)))


    def __init__(self):
        self.context = Context()
        self.rules = Live.RuleSets(self)
        self.inport = None
        self.emitters = []

    # Emitter related functions
    def add_emitter(self, emitter):
        self.emitters.append(emitter)

    def remove_emitter(self, emitter):
        self.emitters.remove(emitter)

    def emit(self, event):
        for emitter in self.emitters:
            emitter.emit(event)

    def send_status(self):
        for emitter in self.emitters:
            emitter.send_status()

    # The poll function called by tornado periodic callback
    def midi_poll(self):
        time_event = self.context.time_event()
        if time_event:
            event = {}
            event['data'] = {
                'type': 'timer',
                'name': time_event
            }
            self.emit(event)

        if self.inport:
            for message in self.inport.iter_pending():
                self.callback(message)

    # Resets everything
    def reset(self):
        self.context.reset()

    # The real callback when there is a MIDI event
    # Called by Live.midi_poll() actually
    def callback(self, message):
        self.context.incoming_message(message)

        # Deal with keystroke triggers
        event = {}
        event['data'] = {
            'type': 'midi',
            'message': {
                'type': message.type,
                'channel': message.channel,
                'note': message.note if hasattr(message, 'note') else None,
                'velocity': message.velocity if hasattr(message, 'velocity') else None,
                'control': message.control if hasattr(message, 'control') else None,
                'value': message.value if hasattr(message, 'value') else None,
                'time': message.time,
                'note_display': str(Note(message.note)) if hasattr(message, 'note') else '',
            },
            'context': {
                'notes': [str(note) for note in sorted(self.context.notes)],
                'pedal': self.context.pedal,
            }
        }
        self.emit(event)

        if self.rules.current and message.type.startswith('note'):
            triggered = self.rules.current.examine(self.context)

            for trigger in triggered:
                event = {}
                event['data'] = {
                    'type': 'signal',
                    'name': trigger
                }

                self.emit(event)

                # Special signal
                if trigger == 'reset':
                    self.reset()

    def status(self):
        out = OrderedDict()
        out['device'] = self.inport.name if self.inport else None
        out['ruleset'] = self.rules.current.name if self.rules.current else None

        return out
