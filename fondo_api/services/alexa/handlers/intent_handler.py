import logging

from fondo_api.services.alexa.handlers.abstract_handler import AbstractRequestHandler
from fondo_api.services.alexa.intents.request_loan_intent import RequestLoanIntent

logger = logging.getLogger(__name__)

class IntentHandler(AbstractRequestHandler):
    def __init__(self, data, user_id):
        super().__init__(data, user_id)
        self.intents = {
            'RequestLoan': RequestLoanIntent(data, user_id, self.skill_banner)
        }

    def handle(self):
        intent = self.intents.get(self.data['request']['intent']['name'], None)
        if intent is None:
            raise Exception(405, 'Intent not allowed')
        return intent.handle()