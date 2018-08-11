from enum import Enum

class CardEnum(Enum):
    SIMPLE = "Simple"
    STANDARD = "Standard"
    LINK_ACCOUNT = "LinkAccount"
    ASK_FOR_PERMISSIONS = "AskForPermissionsConsent"

class SpeechEnum(Enum):
    PLAIN_TEXT = "PlainText"
    SSML = "SSML"