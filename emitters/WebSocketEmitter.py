from core.emitter import Emitter


# The WebSocketEmitter for tornado websockets
# Emit all events to all connected sockets
class WebSocketEmitter(Emitter):
    def __init__(self):
        self._sockets = []

    def add_websocket(self, socket):
        self._sockets.append(socket)

    def remove_websocket(self, socket):
        self._sockets.remove(socket)

    def emit(self, event):
        for socket in self._sockets:
            socket.write_message(event)
    
    def send_status(self):
        for socket in self._sockets:
            socket.send_status()
