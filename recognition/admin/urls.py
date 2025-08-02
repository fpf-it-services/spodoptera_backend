from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.index, name='dashboard'),
    path('', views.index, name='dashboard'),
    path('get_users/', views.get_users, name='get_users'),    
    path('zones-agro/', views.zone_agro_list, name='zones_agro_list'),
    path('zones-agro/create/', views.create_zone_agro, name='create_zone_agro'),
    path('measures/', views.measures_list, name='measures_list'),
    path('measures/create/', views.create_measure, name='create_measure'),
    path('measures/update/<int:measure_id>/', views.update_measure, name='update_measure'),
    path('measures/delete/<int:measure_id>/', views.delete_measure, name='delete_measure'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]

