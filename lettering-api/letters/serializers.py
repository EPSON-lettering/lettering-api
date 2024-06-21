from rest_framework import serializers
from .models import Letter
from printers.models import EpsonConnectScanData
from matching.models import Match


class LetterSerializer(serializers.Serializer):
    scanData_id = serializers.IntegerField(read_only=True)

    def create(self, validated_data):
        user = self.context['request'].user
        match = Match.objects.get(requester=user)
        ScanData = EpsonConnectScanData.objects.get(id=self.context['scanDataId'])
        letter = Letter.objects.create(
            sender=user,
            receiver=match.acceptor,
            match=match,
            image_url=ScanData['image_url'],
        )
        letter.save()
        return letter
