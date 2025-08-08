from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import TruncDay, TruncMonth
from datetime import datetime, timedelta
from django.contrib import messages
from django.utils import timezone
from recognition.models import UserProfile, Observation, ZoneAgro, CustomUser, CorrectiveMeasure
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
import os

@login_required(login_url='login')
def measures_list(request):
    measures = CorrectiveMeasure.objects.all().order_by('order')
    return render(request, 'pages/measures.html', {'measures': measures})

def create_measure(request):
    if request.method == 'POST':
        order = request.POST.get('order')
        measure = request.POST.get('measure')
        
        if not order or not measure:
            messages.error(request, 'Tous les champs sont obligatoires')
            return redirect('measures_list')
            
        try:
            CorrectiveMeasure.objects.create(
                order=order,
                measure=measure
            )
            messages.success(request, 'Mesure corrective ajoutée avec succès')
        except Exception as e:
            messages.error(request, f'Erreur lors de la création: {str(e)}')
            
    return redirect('measures_list')

def update_measure(request, measure_id):
    if request.method == 'POST':
        measure = CorrectiveMeasure.objects.filter(id=measure_id).first()
        if not measure:
            messages.error(request, 'Mesure non trouvée')
            return redirect('measures_list')
            
        order = request.POST.get('order')
        measure_text = request.POST.get('measure')
        
        if not order or not measure_text:
            messages.error(request, 'Tous les champs sont obligatoires')
            return redirect('measures_list')
            
        try:
            measure.order = order
            measure.measure = measure_text
            measure.save()
            messages.success(request, 'Mesure mise à jour avec succès')
        except Exception as e:
            messages.error(request, f'Erreur lors de la mise à jour: {str(e)}')
            
    return redirect('measures_list')

def delete_measure(request, measure_id):
    if request.method == 'POST':
        measure = CorrectiveMeasure.objects.filter(id=measure_id).first()
        if not measure:
            messages.error(request, 'Mesure non trouvée')
            return redirect('measures_list')
            
        try:
            measure.delete()
            messages.success(request, 'Mesure supprimée avec succès')
        except Exception as e:
            messages.error(request, f'Erreur lors de la suppression: {str(e)}')
            
    return redirect('measures_list')

@login_required(login_url='login')
def zone_agro_list(request):
    zones = ZoneAgro.objects.all()
    return render(request, 'pages/zones_agro.html', {'zones': zones,'active_page': 'zones_agro',})

def create_zone_agro(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        rayon = request.POST.get('rayon')
        try:
            ZoneAgro.objects.create(
                name=name,
                latitude=float(latitude),
                longitude=float(longitude),
                rayon=float(rayon)
            )
            messages.success(request, 'Agro Zone created successfully.')
            return redirect('zones_agro_list')
        except Exception as e:
            messages.error(request, f'Error creating zone: {str(e)}')
            return redirect('zones_agro_list')
    return render(request, 'pages/zones_agro.html')

@login_required(login_url='login')
@login_required(login_url='login')
def index(request):
    total_users = UserProfile.objects.filter(is_admin=False).count()
    total_tests = Observation.objects.count()

    successful_tests = Observation.objects.filter(success=True).count()
    success_percentage = (successful_tests / total_tests * 100) if total_tests > 0 else 0
    failed_percentage = (100 - success_percentage) if total_tests > 0 else 0

    successful_tests_user = Observation.objects.filter(success_according_user=True).count()
    success_according_user_percentage = (successful_tests_user / total_tests * 100) if total_tests > 0 else 0
    failed_according_user_percentage = (100 - success_according_user_percentage) if total_tests > 0 else 0

    tests_by_zone = Observation.objects.values('zone_agro__name').annotate(
        test_count=Count('id')
    ).order_by('zone_agro__name')

    total_tests = max(total_tests, 1)
    tests_by_zone = [
        {
            'zone': item['zone_agro__name'] or 'Sans zone',
            'count': item['test_count'],
            'percentage': (item['test_count'] / total_tests * 100)
        }
        for item in tests_by_zone
    ]

    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    tests_by_day = Observation.objects.filter(
        created_at__range=(start_date, end_date)
    ).annotate(
        day=TruncDay('created_at')
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')

    tests_by_day_data = [
        {
            'day': item['day'].strftime('%Y-%m-%d'),
            'count': item['count']
        }
        for item in tests_by_day
    ]

    users_by_zone = Observation.objects.values('zone_agro__name').annotate(
        user_count=Count('user_profile__id', distinct=True)
    ).order_by('zone_agro__name')

    users_by_zone = [
        {'zone': item['zone_agro__name'] or 'Sans zone', 'count': item['user_count']}
        for item in users_by_zone
    ]

    tests_by_month = Observation.objects.filter(
        created_at__range=(end_date - timedelta(days=365), end_date)
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')

    tests_by_month_data = [
        {
            'month': item['month'].strftime('%Y-%m'),
            'count': item['count']
        }
        for item in tests_by_month
    ]

    last_month = end_date - timedelta(days=30)
    tests_this_month = Observation.objects.filter(
        created_at__year=end_date.year,
        created_at__month=end_date.month
    ).count()

    tests_last_month = Observation.objects.filter(
        created_at__year=last_month.year,
        created_at__month=last_month.month
    ).count()

    growth_percentage = (
        ((tests_this_month - tests_last_month) / tests_last_month * 100)
        if tests_last_month > 0 else 0
    )

    context = {
        'total_users': total_users,
        'total_tests': total_tests,
        'success_percentage': round(success_percentage, 2),
        'failed_percentage': round(failed_percentage, 2),
        'success_according_user_percentage': round(success_according_user_percentage, 2),
        'failed_according_user_percentage': round(failed_according_user_percentage, 2),
        'users_by_zone': users_by_zone,
        'tests_by_zone': tests_by_zone,
        'tests_by_day': tests_by_day_data,
        'tests_by_month': tests_by_month_data,
        'growth_percentage': round(growth_percentage, 2),
        'active_page': 'dashboard',
    }

    return render(request, 'pages/dashboard.html', context)

@login_required(login_url='login')
def get_users(request):
    users = CustomUser.objects.annotate(
        test_count=Count('userprofile__observation')
    ).select_related('userprofile').all()

    context = {
        'users': users,
        'active_page': 'users',
    }

    return render(request, 'pages/users.html', context)


@login_required(login_url='login')
def get_user_images(request, user_id):
    observations = Observation.objects.filter(user_profile__user__id=user_id, image__isnull=False)
    images = [
        {
            'id': obs.id,
            'url': obs.image.url,
            'larval_stage': obs.larval_stage
        }
        for obs in observations
    ]
    return JsonResponse({'images': images})

@login_required(login_url='login')
def delete_images(request):
    if request.method == 'POST':
        image_ids = request.POST.getlist('image_ids')
        user_id = request.POST.get('user_id')
        
        deleted_count = 0
        for image_id in image_ids:
            try:
                observation = Observation.objects.get(id=image_id, user_profile__user__id=user_id)
                if observation.image:
                    if os.path.isfile(observation.image.path):
                        os.remove(observation.image.path)
                observation.image = None
                observation.save()
                deleted_count += 1
            except Observation.DoesNotExist:
                continue

        return JsonResponse({
            'status': 'success',
            'message': f'{deleted_count} image(s) supprimée(s) avec succès.'
        })
    return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée.'}, status=405)


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect')
            return render(request, 'pages/login.html')
    return render(request, 'pages/login.html')


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('login')


@login_required
def profile_view(request):
    total_users = CustomUser.objects.count()
    total_observations = Observation.objects.count()
    total_zones = ZoneAgro.objects.count()
    total_measures = CorrectiveMeasure.objects.count()
    
    return render(request, 'pages/profile.html', {
        'total_users': total_users,
        'total_observations': total_observations,
        'total_zones': total_zones,
        'total_measures': total_measures,
        'active_page': 'profile',
    })

@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.userprofile.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        
        profile = user.userprofile
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        profile.save()
        
        messages.success(request, 'Profil mis à jour avec succès')
        return redirect('profile')
    
    return redirect('profile')
