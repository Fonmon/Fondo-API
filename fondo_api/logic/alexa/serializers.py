from rest_framework import serializers

class OutputSpeechSerializer(serializers.Serializer):
    type = serializers.SerializerMethodField()
    ssml = serializers.CharField(max_length=8000)
    text = serializers.CharField(max_length=8000)

    def get_type(self, obj):
        return obj.type.value

class CardSerializer(serializers.Serializer):
    type = serializers.SerializerMethodField()
    title = serializers.CharField(max_length=8000)
    content = serializers.CharField(max_length=8000)
    text = serializers.CharField(max_length=8000)
    image = serializers.DictField(child=serializers.CharField(max_length=8000))

    def get_type(self, obj):
        return obj.type.value

class ResponseSerializer(serializers.Serializer):
    outputSpeech = OutputSpeechSerializer()
    card = CardSerializer()
    reprompt = OutputSpeechSerializer()
    shouldEndSession = serializers.BooleanField()

class AlexaResponseSerializer(serializers.Serializer):
    version = serializers.CharField(max_length=5)
    response = ResponseSerializer()
