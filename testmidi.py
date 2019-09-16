#!/usr/bin/env python
import os
import sys

from core import live
from core.rules import Rule, RuleSet
from utils.ruleset_loader import ruleset_loader
from emitters import WebSocketEmitter, OSCEmitter, SerialPortEmitter
from rules import BrainCrampTimerRuleSet

import mido
import rtmidi
import tornado.ioloop
from tornado.web import RequestHandler, StaticFileHandler, Application
from tornado.websocket import WebSocketHandler


class IndexHandler(RequestHandler):
    async def get(self):
        self.render('static/index.html')


class ScreenHandler(RequestHandler):
    async def get(self):
        self.render('static/screen.html')


class ScreenSocketHandler(WebSocketHandler):
    def open(self):
        print(f'WebSocket opened... {self}')
        ws_emitter.add_websocket(self)

    def on_message(self, message):
        # print 'got message: %s' % message
        # if message == '%RESET':
        #     midiserver.reset()
        # elif message.startswith('%LISTEN'):
        #     parts = message.split(' ')

        #     if parts[1] == 'START':
        #         if parts[2] == 'COUNTERCLOCK':
        #             print "LISTEN TO COUNTERCLOCK"
        #             midiserver.processor.set_ruleset(midiserver.rs1)
        #         elif parts[2] == 'AIYO':
        #             print "LISTEN TO AIYO"
        #             midiserver.processor.set_ruleset(midiserver.rs2)

        #         midiserver.reset()
        #         midiserver.listen = True
        #     elif parts[1] == 'STOP':
        #         print "LISTEN STOP"
        #         midiserver.reset()
        #         midiserver.listen = False
        pass

    def on_close(self):
        print(f'WebSocket closed... {self}')
        ws_emitter.remove_websocket(self)


if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.realpath(__file__))
    DEFAULT_RULES_DIR = os.path.join(BASE_DIR, 'rules-enabled')

    devices = mido.get_input_names()
    print(devices)
    print(devices[0], type(devices[0]))

    # This is how you use the default loader
    # rule_sets = ruleset_loader(DEFAULT_RULES_DIR)
    # live.rule_set = rule_sets[0]

    # But the BrainCramp needs timer
    live.rule_set = BrainCrampTimerRuleSet.load(os.path.join(DEFAULT_RULES_DIR, 'braincramp'))

    # Setup MIDI In Port
    device = 'Oxygen 61'
    live.inport = mido.open_input(device)
    midi_loop = tornado.ioloop.PeriodicCallback(live.midi_poll, 25)
    midi_loop.start()


    # Setup Websocket Emitter
    ws_emitter = WebSocketEmitter()
    live.add_emitter(ws_emitter)

    # Setup OSC Emitter
    osc_emitter = OSCEmitter()
    live.add_emitter(osc_emitter)

    # Setup SerialPort Emitter
    sp_emitter = SerialPortEmitter()
    live.add_emitter(sp_emitter)
    sp_emitter.connect()
    sp_connect_loop = tornado.ioloop.PeriodicCallback(sp_emitter.connect, 1000)
    sp_connect_loop.start()


    handlers = [
        (r'/', IndexHandler),
        (r'/screen', ScreenHandler),
        (r'/screen/socket', ScreenSocketHandler),

        (r'/static/(.*)', StaticFileHandler, {'path': 'static'}),
    ]

    app = Application(handlers, debug=True)
    app.listen(8001)


    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        live.inport.close()
        print('quitting...')
        sys.exit()
