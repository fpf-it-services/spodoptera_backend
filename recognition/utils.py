import cv2
import numpy as np
from ultralytics import YOLO
from django.conf import settings
import os

MODEL_PATH = os.path.join(settings.BASE_DIR, 'models/spodoptera.pt')
model = YOLO(MODEL_PATH)

def preprocess_image(image_path):
    """
    Prétraiter l'image : redimensionner à 640x640, sans suppression d'arrière-plan.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Impossible de charger l'image : {image_path}")
    img = cv2.resize(img, (640, 640))
    cv2.imwrite('preprocessed_image.jpg', img) 
    img_array = img / 255.0
    return img_array

# def predict_larval_stage(image_path):
#     """
#     Prédire si l'image contient Spodoptera frugiperda et estimer le stade larvaire.
#     """
#     img_array = preprocess_image(image_path)
#     print(img_array)
#     results = model(source=img_array, save=False)  
#     larval_stage = None
#     confidence = None
    
#     for r in results:
#         if r.boxes is not None and len(r.boxes) > 0:
#             print(f"{len(r.boxes)} objets est détecté") 
#             confidence = float(results[0].boxes.conf[0])
#             larval_stage = estimate_larval_stage(results[0])
#         else: 
#             print("Aucune détection")
#     # if results[0].boxes:
#     #     print(f"Classes : {[int(cls) for cls in results[0].boxes.cls]}")
#     #     print(f"Confidences : {[float(conf) for conf in results[0].boxes.conf]}")


#     return larval_stage, confidence

def predict_larval_stage(image_path):
    """
    Détecter si Spodoptera frugiperda est présent dans l'image.
    """
    img_array = preprocess_image(image_path)
    results = model.predict(source=image_path, save=False) 
    larval_stage = None
    confidence = None
    
    for r in results:
        if r.boxes is not None and len(r.boxes) > 0:
            print(f"{len(r.boxes)} objet(s) détecté(s)")
            # if 1 in [int(cls) for cls in r.boxes.cls]: 
            confs = r.boxes.conf.tolist() if r.boxes.conf is not None else []
            print(confs)
            # confidence = float(max(r.boxes.conf)) if r.boxes.conf else 0.0
            larval_stage = "Spodoptera détecté"
            # else:
                # print("Aucune détection de Spodoptera frugiperda")
        else:
            # print("Aucune détection")
            print("Aucune détection de Spodoptera frugiperda")
    
    if larval_stage is None:
        larval_stage = "Aucun Spodoptera détecté"
        confidence = None
    
    return larval_stage, confidence
