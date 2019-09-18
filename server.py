#!/usr/bin/env python
import os
import sys
import argparse
import json

from core import live
from core.rules import Rule, RuleSet
from utils.ruleset_loader import ruleset_loader
from emitters import WebSocketEmitter, OSCEmitter, SerialPortEmitter
from rules import BrainCrampTimerRuleSet, Demo2TimerRuleSet

import mido
import rtmidi
import tornado.ioloop
from tornado.web import RequestHandler, StaticFileHandler, Application
from tornado.websocket import WebSocketHandler


class ScreenHandler(RequestHandler):
    async def get(self):
        self.render('static/screen.html', stage_mode=args.stage, ruleset_dir=DEFAULT_RULES_DIR)


class StatusHandler(RequestHandler):
    async def get(self):
        self.write(json.dumps(live.status()))


class ScreenSocketHandler(WebSocketHandler):
    def open(self):
        print(f'WebSocket opened from {self.request.remote_ip}')
        ws_emitter.add_websocket(self)

        # Send current live status to the console once it is connected
        self.send_status()

    def on_message(self, message):
        print(f'WebSocket got message: {message}')
        try:
            packet = json.loads(message)
            packet_type = packet.get('type', None)

            if packet_type == 'action':
                action = packet.get('action', None)

                if action == 'change_ruleset':
                    name = packet.get('name', None)
                    live.rules.set_current(name)

                if action == 'trigger':
                    name = packet.get('name', None)
                    event = {}
                    event['data'] = {
                        'type': 'signal',
                        'name': name
                    }

                    live.emit(event)

        except json.decoder.JSONDecodeError:
            pass

    def on_close(self):
        print(f'WebSocket closed from {self.request.remote_ip}')
        ws_emitter.remove_websocket(self)

    def send_status(self):
        event = {
            'data': {
                'type': 'status',
                'status': live.status()
            },
        }
        self.write_message(event)


def list_devices(devices):
    if devices:
        print('Available MIDI devices:')
        for device in devices:
            print(device)
    else:
        print('No available MIDI devices.')


def reload_hook():
    print('Code changed! Reload server...\n\n')


if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.realpath(__file__))
    DEFAULT_RULES_DIR = os.path.join(BASE_DIR, 'rules-enabled')

    # Special stuff here, stage mode
    # If there is a file ".stage", stage mode is auto on
    stage_default = os.path.isfile(os.path.join(BASE_DIR, '.stage'))

    parser = argparse.ArgumentParser(description='Live Spring Server')
    parser.add_argument('-p', '--port', type=int, default=8001, help='The port that the server listens to, default to 8001.')
    parser.add_argument('-l', '--list', action='store_true', help='List the MIDI devices.')
    parser.add_argument('-m', '--midi', default='0', help='Indicate which MIDI device to use. '\
                                                          'Specify the name listed by the `-l` '\
                                                          'command or simply use the 0-based index '\
                                                          'returned by the list. Defaults to the '\
                                                          'first returned from the list.')
    parser.add_argument('-s', '--stage', default=stage_default, action='store_true', help='Stage Mode (won\'t show the initial screen)')

    args = parser.parse_args()

    devices = mido.get_input_names()

    # The -l command
    if args.list:
        list_devices(devices)
        sys.exit(0)


    # Resolve the -m argument.
    device = None
    if len(devices):
        # Try to retrieve the midi input. See if it is 0-based index first
        try:
            index = int(args.midi)
            if index < 0:
                print(f'The index you specified must be 0 or a positive number.')
                sys.exit(-1)

            device = devices[index]
        except ValueError:
            pass
        except IndexError:
            if len(devices) > 1:
                print(f'There are only {len(devices)} devices. The index you specified is out of range.')
                sys.exit(-1)
            elif len(devices) == 1:
                print(f'There is only one device. The index you specified is out of range.')
                sys.exit(-1)

        # Second pass, check if the name matches any device here
        if not device:
            device = args.midi

            if device not in devices:
                print(f'No MIDI device {args.midi}')
                sys.exit(-1)

    else:
        # No MIDI device found.
        print(f'No MIDI device detected. Continue without MIDI input')


    # This is how you use the default loader
    # rule_sets = ruleset_loader(DEFAULT_RULES_DIR)
    # live.rules.load(rule_sets)
    # live.rules.set_default()


    # But the BrainCramp needs timer, it needs to be loaded by its own rule set class
    live.rules.add(BrainCrampTimerRuleSet.load(os.path.join(DEFAULT_RULES_DIR, 'braincramp')), current=True)

    # Load other rule sets
    live.rules.add(RuleSet.load(os.path.join(DEFAULT_RULES_DIR, 'cakewalk')))
    live.rules.add(RuleSet.load(os.path.join(DEFAULT_RULES_DIR, 'demo1')))
    live.rules.add(Demo2TimerRuleSet.load(os.path.join(DEFAULT_RULES_DIR, 'demo2')))

    print('')

    # Setup MIDI In Port
    if device:
        print(f'Listening to MIDI events from device {device}')
        live.inport = mido.open_input(device)
        midi_loop = tornado.ioloop.PeriodicCallback(live.midi_poll, 25)
        midi_loop.start()


    # Setup Websocket Emitter
    ws_emitter = WebSocketEmitter()
    live.add_emitter(ws_emitter)

    # Super ugly. In order to do something special in demo2,
    # this ruleset emits bar timestamps directly to the websocket
    # So we need to inject the ws_emitter here
    live.rules.sets['demo2'].attach_ws_emitter(ws_emitter)

    # Setup OSC Emitter
    osc_emitter = OSCEmitter()
    live.add_emitter(osc_emitter)

    # Setup SerialPort Emitter
    sp_emitter = SerialPortEmitter()
    live.add_emitter(sp_emitter)
    sp_emitter.connect()
    sp_connect_loop = tornado.ioloop.PeriodicCallback(sp_emitter.connect, 1000)
    sp_connect_loop.start()


    # Setting up tornado routes
    handlers = [
        (r'/', ScreenHandler),
        (r'/socket', ScreenSocketHandler),
        (r'/status', StatusHandler),
        (r'/static/(.*)', StaticFileHandler, {'path': 'static'}),
    ]

    url = 'http://127.0.0.1' if args.port == 80 else f'http://127.0.0.1:{args.port}'
    print(f'Starting live spring server at port {args.port}...')
    print(f'Visit the console at {url}')
    app = Application(handlers, debug=True)
    app.listen(args.port)

    tornado.autoreload.add_reload_hook(reload_hook)

    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        if live.inport:
            live.inport.close()
        print('quitting...')
        sys.exit()
