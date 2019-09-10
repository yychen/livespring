NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
NOTES_COUNT = len(NOTES)

class Note:
    def __init__(self, data):
        if type(data) is int:
            self.data = data
            self.note = NOTES[data % NOTES_COUNT]
            self.height = int(data / NOTES_COUNT)
        elif type(data) is str:
            self.note = data[:-1]

            if self.note not in NOTES:
                raise TypeError('Invalid note')

            self.height = int(data[-1])
            self.data = self.height * NOTES_COUNT + NOTES.index(self.note)

        else:
            raise NotImplemented

    def __lt__(self, other):
        if not isinstance(other, Note):
            return NotImplemented

        return self.data < other.data

    def __eq__(self, other):
        if type(other) == str:
            return str(self) == other
        elif not isinstance(other, Note):
            return NotImplemented

        return self.data == other.data

    def __hash__(self):
        return str(self).__hash__()

    def __str__(self):
        return f'{self.note}{self.height}'
    
    def __repr__(self):
        return f'Note({self.note}{self.height})'
