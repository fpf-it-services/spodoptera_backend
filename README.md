# Spodoptera Detection App - Documentation mise à jour

## Description
L'application Spodoptera Detection est une solution web basée sur Django et Django REST Framework pour détecter la présence du ravageur agricole *Spodoptera frugiperda* dans les images. Elle combine un modèle YOLO optimisé avec une interface API simple et une gestion utilisateur complète.

## Nouveautés et améliorations
- Système d'authentification et de gestion des utilisateurs
- Géolocalisation des observations
- Historique des détections
- Validation manuelle des résultats
- Interface administrateur

## Fonctionnalités principales

### Pour les utilisateurs
- **Détection de Spodoptera** via upload d'images
- **Géolocalisation** automatique des observations
- **Historique** des analyses
- **Validation manuelle** des résultats
- **Recommandations** personnalisées

### Pour les administrateurs
- **Tableau de bord** des détections
- **Gestion** des utilisateurs
- **Édition** des mesures correctives
- **Statistiques** d'utilisation

## Installation

### Prérequis
- Python 3.10+
- PostgreSQL (recommandé) ou SQLite
- Git

### Configuration initiale

```bash
# Cloner le dépôt
git clone https://github.com/fpf-it-services/spodoptera_backend.git
cd spodoptera_backend

# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  
venv\Scripts\activate    

# Installer les dépendances
pip install -r requirements.txt
```

### Configuration de la base de données
1. Créer un fichier `.env` à la racine:
```ini
DATABASE_URL=postgres://user:password@localhost/spodoptera
SECRET_KEY=votre_secret_key_ici
DEBUG=True
```

2. Appliquer les migrations:
```bash
python manage.py migrate
```

### Chargement des données initiales
```bash
python manage.py loaddata initial_measures.json
```

## API Endpoints

### Authentification
- `POST /api/register/` - Enregistrement utilisateur
- `POST /api/register-admin/` - Enregistrement administrateur

### Détection
- `POST /api/predict/` - Soumettre une image pour analyse

### Gestion
- `POST /api/update-test-success/` - Valider/invalider une détection

## Modèles de données

### UserProfile
- `user` - Lien vers l'utilisateur Django
- `last_name` - Nom de famille
- `is_admin` - Statut administrateur

### Observation
- `user_profile` - Utilisateur associé
- `image` - Image analysée
- `larval_stage` - Résultat de la détection
- `latitude/longitude` - Coordonnées GPS
- `zone_agro` - Zone agroécologique calculée
- `success` - Détection automatique
- `success_according_user` - Validation manuelle

### CorrectiveMeasure
- `larval_stage` - Stade larvaire cible
- `measure` - Texte de la mesure
- `order` - Ordre d'affichage

## Exemples de requêtes

### Enregistrement utilisateur
```bash
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Jean", "last_name":"Dupont"}'
```

### Soumission d'une image
```bash
curl -X POST http://localhost:8000/api/predict/ \
  -F "user_id=1" \
  -F "image=@/chemin/vers/image.jpg" \
  -F "latitude=12.34" \
  -F "longitude=56.78"
```

### Validation manuelle
```bash
curl -X POST http://localhost:8000/api/update-test-success/ \
  -H "Content-Type: application/json" \
  -d '{"user_id":1, "observation_id":5, "success_according_user":true}'
```

## Réponses API

### Réponse réussie (détection)
```json
{
  "success": true,
  "test_id": 42,
  "corrective_measures": [
    "Appliquez un traitement biologique dans les 48h"
  ],
  "confidence": 0.92
}
```

### Réponse sans détection
```json
{
  "success": false,
  "test_id": 43,
  "corrective_measures": [],
  "confidence": null
}
```

## Gestion administrative

### Accès à l'interface admin
1. Créer un superutilisateur:
```bash
python manage.py createsuperuser
```



```

2. Configurer un serveur WSGI (ex: Gunicorn + Nginx)

### Variables d'environnement critiques
- `DATABASE_URL` - URL de connexion à la base
- `SECRET_KEY` - Clé secrète Django
- `YOLO_MODEL_PATH` - Chemin vers le modèle YOLO
- `FASTAPI_URL` - URL du service de détection

## Maintenance

### Sauvegardes
```bash
python manage.py dumpdata --indent=2 > backup.json
```

### Mises à jour
```bash
git pull origin main
pip install -r requirements.txt
python manage.py migrate
```


