from abc import ABC, abstractmethod

class AbstractRequestHandler(ABC):
    def __init__(self, data, user_id):
        self.data = data
        self.user_id = user_id

    @abstractmethod
    def handle(self):
        pass
