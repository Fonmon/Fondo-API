from abc import ABC, abstractmethod

class AbstractExecuter(ABC):
    @abstractmethod
    def run(self, payload):
        pass