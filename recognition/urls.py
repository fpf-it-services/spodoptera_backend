from django.urls import path
from .views import PredictLarvalStage

urlpatterns = [
    path('predict/', PredictLarvalStage.as_view(), name='predict_larval_stage'),
]
