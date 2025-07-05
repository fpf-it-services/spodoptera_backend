from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ObservationSerializer
from .utils import predict_larval_stage
from .models import Observation, CorrectiveMeasure

class PredictLarvalStage(APIView):
    def post(self, request):
        serializer = ObservationSerializer(data=request.data)
        if serializer.is_valid():
            observation = serializer.save()
            detection_result, confidence = predict_larval_stage(observation.image.path)
            observation.larval_stage = detection_result 
            observation.save()
            success = detection_result == "Spodoptera détecté"
            measures = CorrectiveMeasure.objects.filter(larval_stage="Spodoptera détecté").values_list('measure', flat=True) if success else []
            response_data = {
                'observation': ObservationSerializer(observation).data,
                'confidence': confidence,
                'success': success,
                'corrective_measures': list(measures) if measures else []
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    