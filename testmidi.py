#!/usr/bin/env python
import os
import sys

from core import live
from core.rules import Rule, RuleSet
from utils.ruleset_loader import ruleset_loader

import mido
import rtmidi
import tornado.ioloop


if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.realpath(__file__))
    DEFAULT_RULES_DIR = os.path.join(BASE_DIR, 'rules-enabled')

    devices = mido.get_input_names()
    print(devices)
    print(devices[0], type(devices[0]))

    rule_sets = ruleset_loader(DEFAULT_RULES_DIR)
    print(rule_sets)
    live.rule_set = rule_sets[0]


    device = 'Oxygen 61'
    inport = mido.open_input(device, callback=live.callback)
    loop = tornado.ioloop.IOLoop.current()

    try:
        loop.start()
    except KeyboardInterrupt:
        inport.close()
        print('quitting...')
        sys.exit()
