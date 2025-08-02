import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ObservationSerializer, UserLoginSerializer, UserRegisterSerializer
from .utils import detect_zone_from_coordinates
from .models import CorrectiveMeasure, Observation, UserProfile
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token
import os

User = get_user_model()

# Configuration de l'URL de l'API FastAPI
FASTAPI_URL = os.getenv('FASTAPI_URL', 'http://localhost:7860')

class PredictLarvalStage(APIView):
    def post(self, request): 
        user_id = request.data.get("user_id")
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur non trouvé'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ObservationSerializer(data=request.data)
        if serializer.is_valid():
            observation = serializer.save()
            observation.user_profile = user.userprofile 
            try:
                with open(observation.image.path, 'rb') as img_file:
                    files = {'file': (observation.image.name, img_file, 'image/jpeg')}
                    response = requests.post(f"{FASTAPI_URL}/predict/", files=files)
                if response.status_code != 200:
                    raise Exception(f"Erreur API FastAPI: {response.text}")
                
                api_result = response.json()
                
                observation.larval_stage = api_result.get('larval_stage', 'Aucun Spodoptera détecté')
                observation.success = (api_result.get('larval_stage') == "Spodoptera détecté")
                confidence = api_result.get('confidence')
                
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            if observation.latitude and observation.longitude:
                observation.zone_agro = detect_zone_from_coordinates(
                    observation.latitude,
                    observation.longitude
                )

            # Sauvegarder l'observation
            observation.save()
            measures = []
            if observation.success:
                measures = CorrectiveMeasure.objects.filter(
                    larval_stage=observation.larval_stage
                ).values_list('measure', flat=True)

            return Response({
                'success': observation.success,
                'test_id': observation.id,
                'corrective_measures': list(measures),
                'confidence': confidence
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateTestSuccessView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        test_id = request.data.get('observation_id')
        success_user = request.data.get('success_according_user')

        if user_id is None or test_id is None or success_user is None:
            return Response({"error": "Tous les champs sont requis."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_profile = UserProfile.objects.get(user_id=user_id)
            observation = Observation.objects.get(id=test_id, user_profile=user_profile)
            observation.success_according_user = success_user
            observation.save()
            return Response({"message": "Observation mise à jour avec succès."}, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({"error": "Profil utilisateur introuvable."}, status=status.HTTP_404_NOT_FOUND)
        except Observation.DoesNotExist:
            return Response({"error": "Observation introuvable."}, status=status.HTTP_404_NOT_FOUND)



class RegisterAPIView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'user': {
                    'id': user.id,
                    'last_name': user.userprofile.last_name,
                    'first_name': user.first_name,
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                request,
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            if user:
                login(request, user)
                token, created = Token.objects.get_or_create(user=user)
                return Response({
                    'token': token.key,
                    'user': {
                        'username': user.username,
                        'email': user.email,
                        'last_name': user.userprofile.last_name,
                        'first_name': user.userprofile.first_name,
                        'zone_agro_select': user.userprofile.zone_agro_select
                    }
                }, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
