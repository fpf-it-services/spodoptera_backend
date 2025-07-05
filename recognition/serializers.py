# from rest_framework import serializers
# from .models import Observation, AgroEcologicalZone

# class ObservationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Observation
#         fields = ['id', 'zone', 'rainfall', 'temperature', 'maize_stage', 'image', 'larval_stage', 'created_at']

from rest_framework import serializers
from .models import Observation

class ObservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Observation
        fields = ['id', 'image', 'larval_stage', 'created_at']