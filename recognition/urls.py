from django.urls import path
from .views import PredictLarvalStage, RegisterAPIView, LoginAPIView, UpdateTestSuccessView

urlpatterns = [
    path('predict/', PredictLarvalStage.as_view(), name='predict_larval_stage'),
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('register-admin/', AdminRegisterAPIView.as_view(), name='register_admin'),
    path('update-test-success/', UpdateTestSuccessView.as_view(), name='update-test-success'),

    # path('login/', LoginAPIView.as_view(), name='login'),
]
