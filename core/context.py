from .note import Note

class Context(object):
    def __init__(self):
        self.notes = set()
        self.pedal = False

    def incoming_message(self, msg):
        if msg.type == 'note_on':
            self.notes.add(Note(msg.note))
        elif msg.type == 'note_off':
            self.notes.remove(Note(msg.note))
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
