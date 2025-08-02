from django.db import models
from django.contrib.auth.models import AbstractUser

class ZoneAgro(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    rayon = models.FloatField(help_text="Rayon en mètres autour du point central") 

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    # username = None
    email = models.EmailField(blank=True, null=True, unique=False)
    first_name = models.CharField(max_length=100, unique=True) 
    USERNAME_FIELD = 'first_name'
    REQUIRED_FIELDS = ['username'] 

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)  
    last_name = models.CharField(max_length=100)
    is_admin = models.BooleanField(default=False, help_text="Indique si l'utilisateur est un administrateur")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name} {self.last_name}"


class Observation(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='images/')
    larval_stage = models.CharField(max_length=100)
    confidence = models.FloatField(null=True, blank=True)
    zone_agro = models.ForeignKey(ZoneAgro, on_delete=models.SET_NULL, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)
    success_according_user = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return f"Test {self.id} - {self.larval_stage}"


class CorrectiveMeasure(models.Model):
    """
    Modèle pour stocker les mesures correctives associées à chaque stade larvaire de Spodoptera frugiperda.
    """
    larval_stage = models.CharField(max_length=50, help_text="Stade larvaire (ex: L1, L2, ...)")
    measure = models.TextField(help_text="Mesure corrective ou conseil à suivre")

    def __str__(self):
        return f"Measure for {self.larval_stage}"