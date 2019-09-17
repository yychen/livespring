#!/usr/bin/env python
import sys
import os
import argparse

# not sure if this is a good idea
BASE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
sys.path.insert(1, BASE_DIR)

from emitters import SerialPortEmitter

parser = argparse.ArgumentParser()
parser.add_argument("command", choices=['control'])
parser.add_argument("arg", nargs='?', metavar='control argument', type=int)

args = parser.parse_args()

if args.command == 'control' and not args.arg:
    if not args.arg:
        raise ValueError('control argument needed when using the control command')

emitter = SerialPortEmitter()
emitter.connect()
emitter.command(args.command, args.arg)
emitter.close()
