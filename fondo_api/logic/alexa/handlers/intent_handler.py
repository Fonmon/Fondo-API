from .abstract_handler import AbstractRequestHandler
from ..model.models import AlexaResponse, Directive
from ..serializers import AlexaResponseSerializer
from ..model.enums import SpeechEnum, CardEnum

class IntentHandler(AbstractRequestHandler):
    def __init__(self, data):
        super().__init__(data)
        self.intents = [
            'RequestLoan'
        ]

    def handle(self):
        complete = self.isComplete()
        text = ""
        if complete:
            text = "We have finished"
        response = AlexaResponse(complete)\
            .set_card(CardEnum.STANDARD, "Fake intent", "Fake content intent", "Fake text intent")\
            .add_image_to_card("https://fonmon.minagle.com/static/media/ffm_256.d76444a7.png","https://fonmon.minagle.com/static/media/ffm_256.d76444a7.png")\
            .add_directive(Directive("Dialog.Delegate"))
            
        serializer = AlexaResponseSerializer(response)
        return serializer.data

    def isComplete(self):
        slots = self.data['request']['intent']['slots']
        for slot in slots:
            if "value" not in slots[slot]:
                return False
        return True