from .note import Note

from collections import deque
from datetime import datetime


class TimeTrigger(object):
    def __init__(self, timestamp, trigger):
        self.timestamp = timestamp
        self.trigger = trigger


class Context(object):
    def __init__(self):
        self.reset()

    def reset(self):
        self.notes = set()
        self.pedal = False

        self.time_triggers = deque(maxlen=32)
        self.time_trigger_next = None

    def time_event(self):
        now = datetime.now()
        if self.time_trigger_next:
            if now > self.time_trigger_next.timestamp:
                trigger = self.time_trigger_next.trigger

                try:
                    self.time_trigger_next = self.time_triggers.popleft()
                except IndexError:
                    self.time_trigger_next = None

                return trigger

        return None

    def incoming_message(self, msg):
        if msg.type == 'note_on':
            self.notes.add(Note(msg.note))
        elif msg.type == 'note_off':
            try:
                self.notes.remove(Note(msg.note))
            except KeyError:
                # Don't do anything if the note is not in there, just ignore it.
                pass
        elif msg.type == 'control_change':
            if msg.control == 64:
                self.pedal = msg.value == 127

        print(self)

    def __str__(self):
        notes = " ".join(str(e) for e in sorted(self.notes))
        pedal = ' _' if self.pedal else ''

        if notes:
            return f'{notes} {pedal}'
        elif pedal:
            return pedal
        else:
            return '(empty)'
