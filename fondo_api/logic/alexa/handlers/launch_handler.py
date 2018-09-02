from .abstract_handler import AbstractRequestHandler
from ..model.models import AlexaResponse
from ..serializers import AlexaResponseSerializer
from ..model.enums import SpeechEnum, CardEnum

class LaunchHandler(AbstractRequestHandler):
    def __init__(self, data, user_id):
        super().__init__(data, user_id)

    def handle(self):
        response = AlexaResponse(False)\
            .set_output_speech(SpeechEnum.PLAIN_TEXT, text="Welcome to family Montañez fund assistant, what can I help you?")\
            .set_card(CardEnum.STANDARD, "Fonmon Voice Assistant", "", "Family assistant for recurring tasks")\
            .add_image_to_card(self.skill_banner, self.skill_banner)
            
        serializer = AlexaResponseSerializer(response)
        return serializer.data