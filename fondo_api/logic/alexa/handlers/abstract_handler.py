import os
from abc import ABC, abstractmethod

class AbstractRequestHandler(ABC):
    def __init__(self, data, user_id):
        self.data = data
        self.user_id = user_id
        self.skill_banner = "https://{}/static/banner.png".format(os.environ.get('ALLOWED_HOST_DOMAIN'))

    @abstractmethod
    def handle(self):
        pass
