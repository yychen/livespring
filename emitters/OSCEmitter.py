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

    def emit(self, event):
        data = event.get('data')
        if data.get('type') == 'signal':
            signal = None
            if data.get('name') == 'led-pattern-1':
                signal = b'\x07'
            elif data.get('name') == 'led-pattern-2':
                signal = b'\x01'
            elif data.get('name') == 'led-pattern-3':
                signal = b'\x08'

            if signal:
                for osc in self._targets:
                    osc.send_message("/control", ord(signal))
