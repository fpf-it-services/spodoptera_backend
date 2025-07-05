# Spodoptera Detection App

## Description
Spodoptera Detection App est une application web développée avec Django et l'API REST Framework pour détecter la présence de *Spodoptera frugiperda* (une espèce de ravageur agricole) dans des images. Utilisant un modèle YOLO (You Only Look Once) entraîné, l'application analyse les images téléchargées et retourne une réponse indiquant si le ravageur est détecté ou non. En cas de détection, des mesures correctives sont fournies pour aider à gérer l'infestation.

Cette application est conçue pour les agriculteurs et les experts agricoles, offrant une solution simple pour surveiller les cultures et prendre des décisions éclairées.

## Fonctionnalités
- **Détection de *Spodoptera frugiperda*** : Analyse des images pour confirmer la présence du ravageur.
- **Mesures correctives** : Fournit des recommandations personnalisées lorsqu'une détection est confirmée.
- **API REST** : Permet l'envoi d'images via une requête POST et retourne des données JSON.
- **Interface légère** : Fonctionne avec un modèle YOLO pré-entraîné et un prétraitement minimal.

## Prérequis
- **Python 3.13** ou version supérieure.
- **Django** : Framework web pour le backend.
- **djangorestframework** : Pour l'API REST.
- **ultralytics** : Pour utiliser le modèle YOLO.
- **OpenCV (cv2)** : Pour le prétraitement des images.
- **NumPy** : Pour manipuler les tableaux d'images.

## Installation

### 1. Cloner le dépôt
```bash
git clone https://github.com/fpf-it-services/spodoptera_backend.git
cd spodoptera_backend
```

### 2. Créer un environnement virtuel
```bash
python -m venv env
source env/bin/activate  # Sur Linux/Mac
env\Scripts\activate     # Sur Windows
```

### 3. Installer les dépendances
Crée un fichier `requirements.txt` avec :
```
django>=4.2
djangorestframework>=3.14
ultralytics>=8.0
opencv-python>=4.5
numpy>=1.21
```
Puis installe-les :
```bash
pip install -r requirements.txt
```

### 4. Configurer le projet
- Copie le fichier `.env.example` (si présent) en `.env` et ajuste les variables si nécessaire.
- Place le modèle YOLO (`spodoptera.pt`) dans le dossier `spodoptera_backend/models/`.

### 5. Appliquer les migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Lancer le serveur
```bash
python manage.py runserver
```

L'application sera accessible à l'adresse `http://127.0.0.1:8000/`.

## Utilisation

### Endpoint API
- **URL** : `/api/predict/`
- **Méthode** : `POST`
- **Corps de la requête** :
  - `image` : Fichier image (format JPEG recommandé, taille originale 2848x2848 pixels recommandée).
- **Exemple de requête avec cURL** :
  ```bash
  curl -X POST -F "image=@/chemin/vers/votre/image.jpg" http://127.0.0.1:8000/api/predict/
  ```

### Réponse JSON
- **Succès (201 Created)** :
  ```json
  {
      "observation": {
          "id": 1,
          "image": "/media/images/test_image.jpg",
          "larval_stage": "Spodoptera détecté",
          "created_at": "2025-07-05T16:30:00Z"
      },
      "confidence": 0.85,
      "success": true,
      "corrective_measures": [
          "Surveiller régulièrement et retirer manuellement les larves si possible. Appliquer un insecticide biologique en cas d'infestation légère. Consulter un expert pour une intervention ciblée."
      ]
  }
  ```
- **Échec (aucune détection)** :
  ```json
  {
      "observation": {
          "id": 1,
          "image": "/media/images/test_image.jpg",
          "larval_stage": "Aucun Spodoptera détecté",
          "created_at": "2025-07-05T16:30:00Z"
      },
      "confidence": null,
      "success": false,
      "corrective_measures": []
  }
  ```

### Spécifications des images
- **Format** : JPEG.
- **Taille recommandée** : 2848x2848 pixels (redimensionnée à 640x640 pour le traitement).
- **Conditions** : Fond blanc en contre-jour pour une détection optimale.

## Configuration du modèle
- Le modèle YOLO (`yolov8_spodoptera.pt`) doit être placé dans `spodoptera_backend/models/`.
- Assurez-vous que le modèle est entraîné pour détecter la classe `1` correspondant à *Spodoptera frugiperda*.

## Ajout de mesures correctives
1. Créez des entrées dans la base de données via l'interface d'administration Django ou un script.
2. Exemple de script (`add_measures.py`) :
   ```python
   from django.core.management.base import BaseCommand
   from recognition.models import CorrectiveMeasure

   class Command(BaseCommand):
       help = 'Ajoute des mesures correctives pour Spodoptera frugiperda'

       def handle(self, *args, **options):
           measures = [
               ("Spodoptera détecté", "Surveiller régulièrement et retirer manuellement les larves si possible. Appliquer un insecticide biologique en cas d'infestation légère. Consulter un expert pour une intervention ciblée."),
           ]
           for stage, measure in measures:
               CorrectiveMeasure.objects.get_or_create(larval_stage=stage, measure=measure)
           self.stdout.write(self.style.SUCCESS('Mesures ajoutées avec succès'))

   ```
   Exécutez-le avec :
   ```bash
   python manage.py add_measures
   ```
