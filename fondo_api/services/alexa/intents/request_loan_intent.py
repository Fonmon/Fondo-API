import logging

from fondo_api.services.alexa.model.models import AlexaResponse, Directive
from fondo_api.services.alexa.model.enums import SpeechEnum, CardEnum
from fondo_api.services.alexa.serializers import AlexaResponseSerializer
from fondo_api.services.loan import LoanService
from fondo_api.services.user import UserService
from fondo_api.services.notification import NotificationService

logger = logging.getLogger(__name__)

class RequestLoanIntent:
    def __init__(self, data, user_id, skill_banner):
        self.data = data
        self.user_id = user_id
        self.skill_banner = skill_banner
        self.__loan_service = LoanService(UserService(), NotificationService())

    def handle(self):
        complete, loan_or_intent = self.process_slots()
        response = AlexaResponse()
        
        if 'dialogState' in self.data['request'] and self.data['request']['dialogState'] == 'COMPLETED':
            success, message = self.__loan_service.create_loan(self.user_id, loan_or_intent)
            if success:
                message = 'Loan has been created successfully, its number is {}'.format(message)
            response.set_output_speech(SpeechEnum.PLAIN_TEXT, text=message)\
                    .set_card(CardEnum.STANDARD, "Request a loan", "", message)\
                    .add_image_to_card(self.skill_banner, self.skill_banner)\
                    .set_shouldEndSession(True)
        else:
            directive = Directive("Dialog.Delegate")
            if not complete:
                directive.add_updated_intent(loan_or_intent)
            response.add_directive(directive)
            
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
                    intent['slots'][slot].pop('value')
                    intent['slots'][slot].pop('resolutions')
                    return (False, intent)
            elif "value" not in slots[slot]:
                return (False, intent)
            elif slots[slot]['value'] == '?':
                intent['slots'][slot].pop('value')
                intent['slots'][slot].pop('source')
                return (False, intent)
            else:
                if slot == 'disbursement_date':
                    value_slot = slots[slot]['value']
                else:
                    value_slot = int(slots[slot]['value'])
            loan_obj[slot] = value_slot
        return (True, loan_obj)