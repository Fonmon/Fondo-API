from abc import ABC, abstractmethod

class AbstractRequestHandler(ABC):
    def __init__(self, data):
        self.data = data

    @abstractmethod
    def handle(self):
        pass
