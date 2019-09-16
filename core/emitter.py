from abc import ABC, abstractmethod


class Emitter(ABC):
    @abstractmethod
    def emit(self, event):
        return

    def send_status(self):
        return 
