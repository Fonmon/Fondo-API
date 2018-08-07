from abc import ABC, abstractmethod

class AbstractRequestHandler(ABC):
    def __init__(self, request):
        self.request = request

    @abstractmethod
    def onLaunch(self):
        pass

    @abstractmethod
    def onIntent(self):
        pass

    @abstractmethod
    def onSessionEnded(self):
        pass
