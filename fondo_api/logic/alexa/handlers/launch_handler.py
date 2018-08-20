from .abstract_handler import AbstractRequestHandler
from ..model.models import AlexaResponse
from ..serializers import AlexaResponseSerializer
from ..model.enums import SpeechEnum, CardEnum

class LaunchHandler(AbstractRequestHandler):
    def __init__(self, data):
        super().__init__(data)

    def handle(self):
        response = AlexaResponse(False)\
            .set_output_speech(SpeechEnum.PLAIN_TEXT, text="Welcome to family Montañez fund assistant, what can I help you?")\
            .set_card(CardEnum.STANDARD, "Fake title", "Fake content", "Fake text")\
            .add_image_to_card("https://fonmon.minagle.com/static/media/ffm_256.d76444a7.png","https://fonmon.minagle.com/static/media/ffm_256.d76444a7.png")
            
        serializer = AlexaResponseSerializer(response)
        return serializer.data