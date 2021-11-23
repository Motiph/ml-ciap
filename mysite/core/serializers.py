from django.db import models
from rest_framework import serializers

from .models import AcmeWebhookMessage

class AcmeWebhookMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcmeWebhookMessage
        fields = ('id','payload')