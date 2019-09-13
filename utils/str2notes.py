import re

from core.note import Note


note_re = re.compile(r'[a-gA-G]#?[0-8]')

def str2notes(string):
    matches = note_re.findall(string)
    return [Note(e) for e in matches]
