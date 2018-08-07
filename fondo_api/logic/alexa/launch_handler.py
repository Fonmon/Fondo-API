from .abstract_handler import AbstractRequestHandler

class LaunchHandler(AbstractRequestHandler):
    def onLaunch(self):
        print('hola')