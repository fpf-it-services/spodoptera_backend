import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    ObservationSerializer,
    AdminRegisterSerializer,
    UserRegisterSerializer,
)
from .utils import detect_zone_from_coordinates
from .models import CorrectiveMeasure, Observation, UserProfile
from django.contrib.auth import get_user_model
import os
from django.views.decorators.csrf import csrf_exempt

User = get_user_model()

FASTAPI_URL = os.getenv("FASTAPI_URL", "https://localhost:7860")
HF_TOKEN = os.getenv("HF_TOKEN")


class PredictLarvalStage(APIView):

    @csrf_exempt
    def post(self, request):
        user_id = request.data.get("user_id")
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "Utilisateur non trouvé"}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ObservationSerializer(data=request.data)
        if serializer.is_valid():
            observation = serializer.save(user_profile=user.userprofile)
            observation.user_profile = user.userprofile
            try:
                with open(observation.image.path, "rb") as img_file:
                    files = {"file": (observation.image.name, img_file, "image/jpeg")}
                    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
                    print(headers)
                    print('------------------------------------------------------------------------')
                    try:
                        response = requests.post(
                            f"{FASTAPI_URL}/predict/", 
                            files=files, 
                            headers=headers,
                            timeout=180  
                        )
                        print(response)
                        print('------------------------------------------------------------------------')
                        
                        response.raise_for_status() 
                        
                    except requests.exceptions.RequestException as e:
                        raise Exception(f"Erreur lors de la requête vers l'API FastAPI: {str(e)}")
                    
                    except Exception as e:
                        # Capture toute autre exception inattendue
                        raise Exception(f"Erreur inattendue lors de la communication avec l'API: {str(e)}")


                api_result = response.json()
                print(api_result)

                observation.larval_stage = (
                    "Spodoptera détecté"
                    if api_result.get("larval_stage") == "Spodoptera détecté"
                    else "Aucun Spodoptera détecté"
                )
                observation.success = (
                    api_result.get("larval_stage") == "Spodoptera détecté"
                )
                confidence = api_result.get("confidence")

            except Exception as e:
                return Response(
                    {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            if observation.latitude and observation.longitude:
                observation.zone_agro = detect_zone_from_coordinates(
                    observation.latitude, observation.longitude
                )

            observation.save()
            measures = []
            if observation.success:
                measure = CorrectiveMeasure.objects.order_by("-order").first()
                if measure:
                    measures = [measure.measure]

            return Response(
                {
                    "success": observation.success,
                    "test_id": observation.id,
                    "corrective_measures": measures,
                    "confidence": confidence,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateTestSuccessView(APIView):

    @csrf_exempt
    def post(self, request):
        user_id = request.data.get("user_id")
        test_id = request.data.get("observation_id")
        success_user = request.data.get("success_according_user")

        if user_id is None or test_id is None or success_user is None:
            return Response(
                {"error": "Tous les champs sont requis."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_profile = UserProfile.objects.get(user_id=user_id)
            observation = Observation.objects.get(id=test_id, user_profile=user_profile)
            observation.success_according_user = success_user
            observation.save()
            return Response(
                {"success": True, "message": "Observation mise à jour avec succès."},
                status=status.HTTP_200_OK,
            )
        except UserProfile.DoesNotExist:
            return Response(
                {"success": False, "error": "Profil utilisateur introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Observation.DoesNotExist:
            return Response(
                {"success": False, "error": "Observation introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )


class RegisterAPIView(APIView):

    @csrf_exempt
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "success": True,
                    "user": {
                        "id": user.id,
                        "last_name": user.userprofile.last_name,
                        "first_name": user.first_name,
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminRegisterAPIView(APIView):

    @csrf_exempt
    def post(self, request):
        serializer = AdminRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "first_name": user.first_name,
                        "is_admin": user.userprofile.is_admin,
                    }
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
