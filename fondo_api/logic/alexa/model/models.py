from .enums import CardEnum, SpeechEnum

class Card(object):
    def __init__(self, type, title, content, text):
        if not isinstance(type, CardEnum):
            raise Exception('Type must be instance of CardEnum')
        self.type = type
        self.title = title
        self.content = content
        self.text = text
        self.image = None

    def add_image(self, small_image_url, large_image_url):
        self.image = dict()
        self.image['smallImageUrl'] = small_image_url
        self.image['largeImageUrl'] = large_image_url

class OutputSpeech(object):
    def __init__(self, type, ssml="", text=""):
        if not isinstance(type, SpeechEnum):
            raise Exception('Type must be instance of SpeechEnum')
        self.type = type
        self.ssml = ssml
        self.text = text

class Directive(object):
    def __init__(self, type):
        self.type = type
        self.updatedIntent = None

    def add_updated_intent(self, intent):
        self.updatedIntent = intent
        return self

class Response(object):
    def __init__(self, shouldEndSession=True):
        self.outputSpeech = None
        self.card = None
        self.reprompt = None
        self.directives = []
        self.shouldEndSession = shouldEndSession

class AlexaResponse(object):
    def __init__(self, shouldEndSession=False):
        self.version = "1.0"
        self.response = Response(shouldEndSession=shouldEndSession)
    
    def set_output_speech(self, type, ssml="", text=""):
        self.response.outputSpeech = OutputSpeech(type,ssml,text)
        return self

    def set_card(self, type, title, content, text):
        self.response.card = Card(type,title,content,text)
        return self

    def add_image_to_card(self, small_image_url, large_image_url):
        self.response.card.add_image(small_image_url, large_image_url)
        return self

    def set_reprompt(self, type, ssml="", text=""):
        self.response.reprompt = OutputSpeech(type,ssml,text)
        return self

    def add_directive(self, directive):
        self.response.directives.append(directive)
        return self

    def set_shouldEndSession(self, value):
        self.response.shouldEndSession = value
