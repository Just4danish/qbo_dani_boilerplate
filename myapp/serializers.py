from rest_framework import serializers
from .models import *

class QBODetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = QBODetails
        fields = "__all__"