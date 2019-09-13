from .context import Context
from .rules import Rule, RuleSet
from .note import Note

class Live(object):
    def __init__(self):
        self.context = Context()
        self.rule_set = None
        self.emitters = []

    def add_emitter(self, emitter):
        self.emitters.append(emitter)

    def remove_emitter(self, emitter):
        self.emitters.remove(emitter)

    def emit(self, event):
        for emitter in self.emitters:
            emitter.emit(event)

    def midi_poll(self):
        if self.inport:
            for message in self.inport.iter_pending():
                self.callback(message)

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
                'time': message.time,
                'note_display': str(Note(message.note)) if hasattr(message, 'note') else '',
            },
            'context': {
                'notes': [str(note) for note in sorted(self.context.notes)],
                'pedal': self.context.pedal,
            }
        }
        self.emit(event)

        if isinstance(self.rule_set, RuleSet) and message.type.startswith('note'):
            triggered = self.rule_set.examine(self.context)

            for trigger in triggered:
                event = {}
                event['data'] = {
                    'type': 'signal',
                    'name': trigger
                }

                self.emit(event)
