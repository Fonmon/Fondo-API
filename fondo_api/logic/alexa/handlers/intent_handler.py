from .abstract_handler import AbstractRequestHandler
from ..model.models import AlexaResponse, Directive
from ..serializers import AlexaResponseSerializer
from ..model.enums import SpeechEnum, CardEnum

class IntentHandler(AbstractRequestHandler):
    def __init__(self, data, user_id):
        super().__init__(data, user_id)
        self.intents = [
            'RequestLoan'
        ]

    def handle(self):
        complete, updated_intent = self.isComplete()
        text = ""
        response = AlexaResponse(complete)\
            .set_card(CardEnum.STANDARD, "Fake intent", "Fake content intent", "Fake text intent")\
            .add_image_to_card("https://fonmon.minagle.com/static/media/ffm_256.d76444a7.png","https://fonmon.minagle.com/static/media/ffm_256.d76444a7.png")
        
        if complete:
            # create request, then if the operation was successfully executed, return success message
            print('done')
        else:
            response.add_directive(Directive("Dialog.Delegate").add_updated_intent(updated_intent))
            
        serializer = AlexaResponseSerializer(response)
        return serializer.data

    def isComplete(self):
        intent = self.data['request']['intent']
        slots = intent['slots']
        for slot in slots:
            if "resolutions" in slots[slot]:
                resolutions = slots[slot]['resolutions']
                if "resolutionsPerAuthority" in resolutions and len(resolutions['resolutionsPerAuthority']) == 1 and\
                   resolutions['resolutionsPerAuthority'][0]['status']['code'] == 'ER_SUCCESS_MATCH':
                    continue
                else:
                    del intent['slots'][slot]['value']
                    del intent['slots'][slot]['resolutions']
                    return (False, intent)
            elif "value" not in slots[slot]:
                return (False, intent)
        return (True, None)