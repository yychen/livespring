from core.emitter import Emitter

import serial
import glob


# The SerialPortEmitter
# Only emit specific events to the destination
# It also checks for new connected serial
class SerialPortEmitter(Emitter):
    def __init__(self):
        self._targets = []

    def connect(self):
        current_names = [ser.name for ser in self._targets]
        
        devices = glob.glob('/dev/cu.SLAB_USBtoUART*')
        for device in devices:
            if device not in current_names:
                ser = serial.Serial(device, 9600, dsrdtr=True)
                print('Found a device not in sers! Opening device: %s' % ser.name)
                self._targets.append(ser)

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
            elif data.get('name') == 'led-clear':
                signal = b'\x10'
            elif data.get('name') == 'led-text':
                signal = b'\x02'

            if signal:
                for ser in self._targets:
                    try:
                        ser.write(signal)
                        ser.flush()
                    except OSError:
                        self._target.remove(ser)
