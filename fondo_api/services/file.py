import logging
import datetime
from google.cloud import storage

from fondo_api.models import File
from fondo_api.serializers import FileSerializer

class FileService:
    
    def __init__(self):
        self.__logger = logging.getLogger(__name__)
        self.client = storage.Client()

    def save_file(self, obj):
        file = File(
            type = int(obj["type"]),
            display_name = obj["name"]
        )
        bucket = self.client.get_bucket("fonmon")
        blob = bucket.blob("{}/{}".format(file.get_type_display(), file.display_name.lower()))
        blob_exists = blob.exists()
        blob.upload_from_file(obj["file"], content_type=obj["file"].content_type)
        if not blob_exists:
            file.save()
        # url = blob.generate_signed_url(
        #     version="v4",
        #     expiration=datetime.timedelta(minutes=5),
        #     method="GET",
        # )

    def get_signed_url(self, id):
        try:
            file = File.objects.get(id = id)
            bucket = self.client.get_bucket("fonmon")
            blob = bucket.blob("{}/{}".format(file.get_type_display(), file.display_name.lower()))
            url = blob.generate_signed_url(
                version="v4",
                expiration=datetime.timedelta(minutes=5),
                method="GET",
            )
            return {"url": url}
        except File.DoesNotExist:
            return None

    def get_files(self, type):
        if type == -1:
            files = File.objects.all().order_by('created_at')
        else:
            files = File.objects.filter(type = type).order_by('created_at')
        serializer = FileSerializer(files, many=True)
        return serializer.data