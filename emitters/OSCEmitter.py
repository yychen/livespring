from core.emitter import Emitter

from pythonosc import udp_client


# The OSCEmitter
# Only emit specific events to the destination
class OSCEmitter(Emitter):
    def __init__(self):
        self._targets = [
            udp_client.SimpleUDPClient('192.168.0.11', 8010),
            udp_client.SimpleUDPClient('192.168.0.12', 8010),
            udp_client.SimpleUDPClient('192.168.0.13', 8010),
            udp_client.SimpleUDPClient('192.168.0.14', 8010),
        ]
        self.last = ''

    def emit(self, event):
        data = event.get('data')
        signal = None
        if data.get('type') == 'signal':
            if data.get('name').startswith('led-pattern-1'):
                signal = b'\x07'
            elif data.get('name').startswith('led-pattern-2'):
                signal = b'\x01'
            elif data.get('name').startswith('led-pattern-3'):
                signal = b'\x08'
            elif data.get('name').startswith('led-pattern-4'):
                signal = b'\x04'
            elif data.get('name') == 'led-clear' or data.get('name') == 'reset':
                signal = b'\x10'
            elif data.get('name') == 'led-text':
                signal = b'\x02'

            if signal:
                self.last = data.get('name')

        if data.get('type') == 'midi' and not data.get('context').get('notes'):
            if self.last.endswith('!'):
                signal = b'\x10'
                self.last = ''

        if signal:
            self.command('control', ord(signal))

    def command(self, command, argument=16):
        args = []

        if command == 'shutdown':
            args = ["/shutdown", 1]
        elif command == 'reboot':
            args = ["/reboot", 1]
        elif command == 'beat':
            args = ["/beat", 1]
        elif command == 'control':
            args = ["/control", argument]

        for osc in self._targets:
            try:
                osc.send_message(*args)
            except OSError as e:
                pass
