import logging
from .abstract_handler import AbstractRequestHandler
from ..model.models import AlexaResponse, Directive
from ..serializers import AlexaResponseSerializer
from ..model.enums import SpeechEnum, CardEnum
from ....logic.loan_logic import create_loan

logger = logging.getLogger(__name__)

class IntentHandler(AbstractRequestHandler):
    def __init__(self, data, user_id):
        super().__init__(data, user_id)
        self.intents = [
            'RequestLoan'
        ]

    def handle(self):
        complete, loan_or_intent = self.process_slots()
        response = AlexaResponse()\
            .set_card(CardEnum.STANDARD, "Fake intent", "Fake content intent", "Fake text intent")\
            .add_image_to_card("https://fonmon.minagle.com/static/media/ffm_256.d76444a7.png","https://fonmon.minagle.com/static/media/ffm_256.d76444a7.png")
        
        if 'dialogState' in self.data['request'] and self.data['request']['dialogState'] == 'COMPLETED':
            success, message = create_loan(self.user_id, loan_or_intent)
            if success:
                message = 'Loan has been created successfully, its number is {}'.format(message)
            response.set_output_speech(SpeechEnum.PLAIN_TEXT, text=message)
            response.set_shouldEndSession(True)
        else:
            if complete:
                response.add_directive(Directive("Dialog.Delegate"))
            else:
                response.add_directive(Directive("Dialog.Delegate").add_updated_intent(loan_or_intent))
            
        serializer = AlexaResponseSerializer(response)
        return serializer.data

    def process_slots(self):
        intent = self.data['request']['intent']
        slots = intent['slots']
        loan_obj = {}
        loan_obj['comments'] = "Loan requested by Alexa Skill"
        value_slot = None
        for slot in slots:
            if "resolutions" in slots[slot]:
                resolutions = slots[slot]['resolutions']
                if "resolutionsPerAuthority" in resolutions and len(resolutions['resolutionsPerAuthority']) == 1 and\
                   resolutions['resolutionsPerAuthority'][0]['status']['code'] == 'ER_SUCCESS_MATCH':
                    value_slot = int(resolutions['resolutionsPerAuthority'][0]['values'][0]['value']['id'])
                else:
                    del intent['slots'][slot]['value']
                    del intent['slots'][slot]['resolutions']
                    return (False, intent)
            elif "value" not in slots[slot]:
                return (False, intent)
            else:
                if slot == 'disbursement_date':
                    value_slot = slots[slot]['value']
                else:
                    value_slot = int(slots[slot]['value'])
            loan_obj[slot] = value_slot
        return (True, loan_obj)