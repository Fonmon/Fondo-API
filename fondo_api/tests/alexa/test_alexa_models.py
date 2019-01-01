from django.test import TestCase

from fondo_api.logic.alexa.model.models import *
from fondo_api.logic.alexa.model.enums import *

class AlexaModelTest(TestCase):
    def test_card_error(self):
        try:
            card = Card('Standard', 'New card', '', 'Hello there')
        except:
            pass

    def test_card(self):
        card = Card(CardEnum.STANDARD, 'New card', '', 'Hello there')
        self.assertEqual(card.type, CardEnum.STANDARD)
        self.assertEqual(card.title, 'New card')
        self.assertEqual(card.content, '')
        self.assertEqual(card.text, 'Hello there')
        self.assertIs(card.image, None)

    def test_output_speech_error(self):
        try:
            output_speech = OutputSpeech('PLAIN_TEXT')
        except:
            pass

    def test_output_speech(self):
        output_speech = OutputSpeech(SpeechEnum.PLAIN_TEXT)
        self.assertEqual(output_speech.type, SpeechEnum.PLAIN_TEXT)
        self.assertEqual(output_speech.ssml, '')
        self.assertEqual(output_speech.text, '')

    def test_directive(self):
        directive = Directive('Dialog')
        self.assertEqual(directive.type, 'Dialog')
        self.assertEqual(directive.updatedIntent, None)

    def test_response(self):
        response = Response()
        self.assertEqual(response.outputSpeech, None)
        self.assertEqual(response.card, None)
        self.assertEqual(response.reprompt, None)
        self.assertTrue(response.shouldEndSession)
        self.assertEqual(len(response.directives), 0)

        response = Response(False)
        self.assertEqual(response.outputSpeech, None)
        self.assertEqual(response.card, None)
        self.assertEqual(response.reprompt, None)
        self.assertFalse(response.shouldEndSession)
        self.assertEqual(len(response.directives), 0)

    def test_alexa_response(self): 
        response = AlexaResponse()
        response.set_reprompt(SpeechEnum.PLAIN_TEXT)
        self.assertEqual(response.version, "1.0")
        self.assertFalse(response.response.shouldEndSession)
        self.assertEqual(response.response.reprompt.type, SpeechEnum.PLAIN_TEXT)