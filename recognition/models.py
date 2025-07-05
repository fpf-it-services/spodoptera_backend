from django.db import models

class Observation(models.Model):
    image = models.ImageField(upload_to='images/')
    larval_stage = models.CharField(max_length=50, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Observation {self.id}"
    

class CorrectiveMeasure(models.Model):
    """
    Modèle pour stocker les mesures correctives associées à chaque stade larvaire de Spodoptera frugiperda.
    """
    larval_stage = models.CharField(max_length=50, help_text="Stade larvaire (ex: L1, L2, ...)")
    measure = models.TextField(help_text="Mesure corrective ou conseil à suivre")

    def __str__(self):
        return f"Measure for {self.larval_stage}"