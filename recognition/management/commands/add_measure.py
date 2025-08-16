from django.core.management.base import BaseCommand
from recognition.models import CorrectiveMeasure


class Command(BaseCommand):
    help = "Ajoute des mesures correctives pour Spodoptera frugiperda"

    def handle(self, *args, **options):
        measures = [
            (
                "Spodoptera détecté",
                "Surveiller régulièrement et retirer manuellement les larves si possible. Appliquer un insecticide biologique en cas d'infestation légère. Consulter un expert pour une intervention ciblée.",
            ),
        ]
        for stage, measure in measures:
            CorrectiveMeasure.objects.get_or_create(larval_stage=stage, measure=measure)
        self.stdout.write(self.style.SUCCESS("Mesures ajoutées avec succès"))
