from rest_framework import serializers
from .models import Observation, UserProfile
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError

User = get_user_model()

class ObservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Observation
        fields = ['image', 'latitude', 'longitude']

        

class UserRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=100)
    first_name = serializers.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['first_name', 'email', 'last_name']

    def create(self, validated_data):
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        email = validated_data.get('email', '')

        if User.objects.filter(first_name=first_name).exists():
            raise ValidationError({"first_name": "Ce prénom est déjà utilisé. Veuillez en choisir un autre."})

        user = User.objects.create(first_name=first_name, username=first_name, email=email)
        user.set_unusable_password()
        user.save()

        UserProfile.objects.create(user=user, last_name=last_name)
        return user


# User Login Serializer
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)