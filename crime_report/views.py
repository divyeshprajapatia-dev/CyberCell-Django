from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from django.http import JsonResponse, Http404
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
import logging

from .models import CrimeReport, CrimeCategory, Location, CrimeUpdate, UserProfile
from .forms import (
    UserRegistrationForm, UserProfileForm, CrimeReportForm, 
    LocationForm, CrimeUpdateForm, CrimeStatusUpdateForm, UserTypeUpdateForm,
    UserProfileUpdateForm, ProfileUpdateForm
)
from .decorators import police_or_admin_required, admin_required

# Configure logging
logger = logging.getLogger(__name__)

# Home view
def home(request):
    # Get crime categories
    crime_categories = CrimeCategory.objects.all()[:5]
    
    # Get recent reports that are public or belong to the user
    if request.user.is_authenticated:
        recent_reports = CrimeReport.objects.order_by('-reported_on')[:5]
    else:
        recent_reports = CrimeReport.objects.filter(status='resolved').order_by('-reported_on')[:5]
    
    # Get statistics
    total_reports = CrimeReport.objects.count()
    resolved_reports = CrimeReport.objects.filter(status='resolved').count()
    pending_reports = CrimeReport.objects.filter(status='pending').count()
    investigating_reports = CrimeReport.objects.filter(status='investigating').count()
    
    context = {
        'crime_categories': crime_categories,
        'recent_reports': recent_reports,
        'total_reports': total_reports,
        'resolved_reports': resolved_reports,
        'pending_reports': pending_reports,
        'investigating_reports': investigating_reports,
        'show_all_reports': request.user.is_authenticated,
    }
    return render(request, 'crime_report/home.html', context)

# Authentication views
def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)
        
        if user_form.is_valid() and profile_form.is_valid():
            with transaction.atomic():
                user = user_form.save()
                # The signal automatically creates a UserProfile, so we need to update it instead
                profile = user.profile
                # Update the profile with form data
                profile.phone_number = profile_form.cleaned_data.get('phone_number', '')
                profile.address = profile_form.cleaned_data.get('address', '')
                profile.pincode = profile_form.cleaned_data.get('pincode', '')
                profile.user_type = profile_form.cleaned_data.get('user_type', 'citizen')
                if 'profile_picture' in request.FILES:
                    profile.profile_picture = request.FILES['profile_picture']
                profile.save()
                
                username = user_form.cleaned_data.get('username')
                password = user_form.cleaned_data.get('password1')
                user = authenticate(username=username, password=password)
                login(request, user)
                
                messages.success(request, f'Welcome to CyberCell, {username}! Your account has been created successfully.')
                return redirect('home')
    else:
        user_form = UserRegistrationForm()
        profile_form = UserProfileForm()
    
    return render(request, 'crime_report/register.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserProfileUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            with transaction.atomic():
                user_form.save()
                profile_form.save()
                messages.success(request, 'Your profile has been updated successfully!')
                return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserProfileUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    
    # Get user's reports and updates
    user_reports = CrimeReport.objects.filter(reported_by=request.user).order_by('-reported_on')
    if hasattr(request.user, 'profile') and request.user.profile.user_type in ['police', 'admin']:
        assigned_reports = CrimeReport.objects.filter(assigned_to=request.user).order_by('-reported_on')
    else:
        assigned_reports = None
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_reports': user_reports,
        'assigned_reports': assigned_reports,
    }
    
    return render(request, 'crime_report/profile.html', context)

# Crime Report views
@login_required
def report_crime(request):
    if request.method == 'POST':
        crime_form = CrimeReportForm(request.POST, request.FILES)
        location_form = LocationForm(request.POST)
        
        if crime_form.is_valid() and location_form.is_valid():
            try:
                with transaction.atomic():
                    # Check for existing location
                    location_data = location_form.cleaned_data
                    location, created = Location.objects.get_or_create(
                        city=location_data['city'],
                        state=location_data['state'],
                        area=location_data['area'],
                        pincode=location_data['pincode']
                    )
                    
                    crime_report = crime_form.save(commit=False)
                    crime_report.location = location
                    crime_report.reported_by = request.user
                    crime_report.save()
                    
                    messages.success(request, 'Your crime report has been submitted successfully! Our team will review it shortly.')
                    return redirect('crime_detail', pk=crime_report.pk)
            except Exception as e:
                logger.error(f"Error saving crime report: {str(e)}")
                messages.error(request, "An error occurred while saving your report. Please try again.")
    else:
        crime_form = CrimeReportForm()
        location_form = LocationForm()
    
    return render(request, 'crime_report/report_crime.html', {
        'crime_form': crime_form,
        'location_form': location_form
    })

class CrimeListView(ListView):
    model = CrimeReport
    template_name = 'crime_report/crime_list.html'
    context_object_name = 'reports'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = CrimeReport.objects.all()
        
        # Apply filters
        filters = Q()
        
        category = self.request.GET.get('category')
        if category:
            filters &= Q(category_id=category)
            
        status = self.request.GET.get('status')
        if status:
            filters &= Q(status=status)
            
        city = self.request.GET.get('city')
        if city:
            filters &= Q(location__city__icontains=city)
            
        date_from = self.request.GET.get('date_from')
        if date_from:
            filters &= Q(date_of_crime__gte=date_from)
            
        date_to = self.request.GET.get('date_to')
        if date_to:
            filters &= Q(date_of_crime__lte=date_to)
        
        return queryset.filter(filters).order_by('-reported_on')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = CrimeCategory.objects.all()
        context['filters'] = self.request.GET
        context['locations'] = Location.objects.values('city', 'state').distinct()
        
        # Add statistics
        context['total_reports'] = CrimeReport.objects.count()
        context['resolved_reports'] = CrimeReport.objects.filter(status='resolved').count()
        context['pending_reports'] = CrimeReport.objects.filter(status='pending').count()
        
        return context

class CrimeDetailView(LoginRequiredMixin, DetailView):
    model = CrimeReport
    template_name = 'crime_report/crime_detail.html'
    context_object_name = 'crime'
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not obj.can_view_details(self.request.user):
            raise Http404("You don't have permission to view this report.")
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['updates'] = self.object.updates.all().order_by('-updated_on')
        if self.request.user.profile.user_type in ['police', 'admin']:
            context['update_form'] = CrimeUpdateForm()
        
        # Get similar reports based on category and location
        similar_reports = CrimeReport.objects.filter(
            Q(category=self.object.category) | Q(location__city=self.object.location.city)
        ).exclude(id=self.object.id).order_by('-reported_on')[:5]
        context['similar_reports'] = similar_reports
        
        return context
    
    def post(self, request, *args, **kwargs):
        if not request.user.profile.user_type in ['police', 'admin']:
            messages.error(request, "You don't have permission to update this report.")
            return redirect('crime_detail', pk=self.kwargs['pk'])
            
        self.object = self.get_object()
        update_form = CrimeUpdateForm(request.POST)
        
        if update_form.is_valid():
            update = update_form.save(commit=False)
            update.crime_report = self.object
            update.updated_by = request.user
            update.save()
            messages.success(request, 'Update added successfully!')
        else:
            messages.error(request, 'Error adding update. Please check your input.')
            
        return redirect('crime_detail', pk=self.kwargs['pk'])

# Admin views
@login_required
@police_or_admin_required
def admin_dashboard(request):
    # Get statistics
    total_reports = CrimeReport.objects.count()
    pending_reports = CrimeReport.objects.filter(status='pending').count()
    investigating_reports = CrimeReport.objects.filter(status='investigating').count()
    resolved_reports = CrimeReport.objects.filter(status='resolved').count()
    closed_reports = CrimeReport.objects.filter(status='closed').count()
    
    # Calculate investigating percentage
    investigating_percentage = (investigating_reports / total_reports * 100) if total_reports > 0 else 0
    
    stats = {
        'total_reports': total_reports,
        'pending_reports': pending_reports,
        'investigating_reports': investigating_reports,
        'resolved_reports': resolved_reports,
        'closed_reports': closed_reports,
    }
    
    # Crime by category
    crime_by_category = CrimeCategory.objects.annotate(count=Count('crimereport'))
    
    # Crime by location (city)
    crime_by_location = Location.objects.values('city').annotate(
        count=Count('crimereport')
    ).order_by('-count')[:10]
    
    # Recent reports
    recent_reports = CrimeReport.objects.order_by('-reported_on')[:10]
    
    # Reports assigned to this officer (if police)
    if request.user.profile.user_type == 'police':
        assigned_reports = CrimeReport.objects.filter(
            assigned_to=request.user
        ).order_by('-reported_on')
    else:
        assigned_reports = None
    
    # Calculate location percentages and trends
    total_location_reports = sum(loc['count'] for loc in crime_by_location)
    top_locations = []
    for loc in crime_by_location:
        percentage = (loc['count'] / total_location_reports * 100) if total_location_reports > 0 else 0
        # For demo purposes, generate a random trend between -20 and 20
        import random
        trend = random.randint(-20, 20)
        top_locations.append({
            'city': loc['city'],
            'count': loc['count'],
            'percentage': round(percentage, 1),
            'trend': trend
        })

    # Get total users count for quick actions
    total_users = User.objects.count()

    context = {
        'stats': stats,
        'crime_by_category': crime_by_category,
        'crime_by_location': crime_by_location,
        'recent_reports': recent_reports,
        'assigned_reports': assigned_reports,
        'user_type': request.user.profile.user_type,
        'investigating_percentage': round(investigating_percentage, 1),
        'total_reports': total_reports,
        'pending_reports': pending_reports,
        'investigating_reports': investigating_reports,
        'resolved_reports': resolved_reports,
        'top_locations': top_locations,
        'total_users': total_users,
        'today': timezone.now()
    }
    
    return render(request, 'crime_report/admin_dashboard.html', context)

@login_required
@police_or_admin_required
def manage_reports(request):
    reports = CrimeReport.objects.all()
    
    # Apply filters
    status = request.GET.get('status')
    if status:
        reports = reports.filter(status=status)
    
    category_id = request.GET.get('category')
    if category_id:
        reports = reports.filter(category_id=category_id)
    
    city = request.GET.get('city')
    if city:
        reports = reports.filter(location__city__icontains=city)
    
    # Filter by assigned officer
    if request.user.profile.user_type == 'police':
        # Police officers can only see reports assigned to them
        reports = reports.filter(assigned_to=request.user)
    elif request.user.profile.user_type == 'admin':
        # Admins can filter by officer
        officer_id = request.GET.get('officer')
        if officer_id:
            reports = reports.filter(assigned_to_id=officer_id)
    
    # Pagination
    paginator = Paginator(reports.order_by('-reported_on'), 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    context = {
        'page_obj': page_obj,
        'categories': CrimeCategory.objects.all(),
        'officers': User.objects.filter(profile__user_type='police'),
        'filters': request.GET,
        'user_type': request.user.profile.user_type
    }
    
    return render(request, 'crime_report/manage_reports.html', context)

@login_required
@police_or_admin_required
def update_report_status(request, pk):
    crime = get_object_or_404(CrimeReport, pk=pk)
    update_only = request.GET.get('update_only') == 'true'
    
    if request.method == 'POST':
        with transaction.atomic():
            if update_only:
                update_form = CrimeUpdateForm(request.POST)
                if update_form.is_valid():
                    update = update_form.save(commit=False)
                    update.crime_report = crime
                    update.updated_by = request.user
                    update.save()
                    messages.success(request, 'Case update added successfully!')
                    return redirect('crime_detail', pk=pk)
            else:
                status_form = CrimeStatusUpdateForm(request.POST, instance=crime)
                update_form = CrimeUpdateForm(request.POST)
                
                if status_form.is_valid() and update_form.is_valid():
                    status_form.save()
                    update = update_form.save(commit=False)
                    update.crime_report = crime
                    update.updated_by = request.user
                    update.save()
                    messages.success(request, 'Report status and update added successfully!')
                    return redirect('crime_detail', pk=pk)
    else:
        status_form = CrimeStatusUpdateForm(instance=crime)
        update_form = CrimeUpdateForm()
    
    context = {
        'crime': crime,
        'status_form': status_form,
        'update_form': update_form,
        'update_only': update_only
    }
    
    return render(request, 'crime_report/update_report_status.html', context)

@login_required
@admin_required
def manage_users(request):
    users = User.objects.select_related('profile').all()
    
    # Apply filters
    user_type = request.GET.get('user_type')
    if user_type:
        users = users.filter(profile__user_type=user_type)
    
    search = request.GET.get('search')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(profile__phone_number__icontains=search)
        )
    
    # Get statistics
    user_stats = {
        'total': users.count(),
        'police': users.filter(profile__user_type='police').count(),
        'admin': users.filter(profile__user_type='admin').count(),
        'citizen': users.filter(profile__user_type='citizen').count(),
    }
    
    # Get top reporters
    from django.db.models import Count, Max
    top_reporters = User.objects.annotate(
        report_count=Count('reported_crimes'),
        last_report_date=Max('reported_crimes__reported_on')
    ).filter(report_count__gt=0).order_by('-report_count')[:5]
    
    # Get new users per month
    from django.db.models.functions import TruncMonth
    new_users_by_month = User.objects.annotate(
        month=TruncMonth('date_joined')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('-month')[:6]
    
    months = [item['month'].strftime('%b %Y') for item in new_users_by_month][::-1]
    new_users_data = [item['count'] for item in new_users_by_month][::-1]
    
    # Pagination
    paginator = Paginator(users.order_by('-date_joined'), 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    # Get UserProfile objects directly
    user_profiles = UserProfile.objects.select_related('user').all()
    
    # Apply filters to UserProfile queryset
    if user_type:
        user_profiles = user_profiles.filter(user_type=user_type)
    
    if search:
        user_profiles = user_profiles.filter(
            Q(user__username__icontains=search) |
            Q(user__email__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(phone_number__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(user_profiles.order_by('-user__date_joined'), 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    context = {
        'page_obj': page_obj,
        'filters': request.GET,
        'user_types': [('police', 'Police Officer'), ('admin', 'Administrator'), ('citizen', 'Citizen')],
        'user_stats': user_stats,
        'citizen_count': user_stats['citizen'],
        'police_count': user_stats['police'],
        'admin_count': user_stats['admin'],
        'top_reporters': top_reporters,
        'months': str(months).replace("'", '"'),
        'new_users_data': str(new_users_data)
    }
    
    return render(request, 'crime_report/manage_users.html', context)

@login_required
@admin_required
def update_user_type(request, pk):
    user = get_object_or_404(User, pk=pk)
    
    try:
        user_profile = user.profile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile(user=user)
        user_profile.save()
    
    if request.method == 'POST':
        form = UserTypeUpdateForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, f'User type updated for {user.username}!')
            return redirect('manage_users')
    else:
        form = UserTypeUpdateForm(instance=user_profile)
    
    context = {
        'form': form,
        'user': user
    }
    
    return render(request, 'crime_report/update_user_type.html', context)

# API views
@login_required
def crime_stats_api(request):
    if not request.user.profile.user_type in ['police', 'admin']:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Crime by category
    crime_by_category = list(
        CrimeCategory.objects.annotate(count=Count('crimereport')).values('name', 'count')
    )
    
    # Crime by location (city)
    crime_by_location = list(
        Location.objects.values('city').annotate(count=Count('crimereport')).order_by('-count')[:10]
    )
    
    # Crime by status
    crime_by_status = [
        {'status': status[1], 'count': CrimeReport.objects.filter(status=status[0]).count()}
        for status in CrimeReport.STATUS_CHOICES
    ]
    
    # Crime by month (last 12 months)
    now = timezone.now()
    crime_by_month = []
    
    for i in range(12):
        month = now.month - i
        year = now.year
        if month <= 0:
            month += 12
            year -= 1
        
        count = CrimeReport.objects.filter(
            reported_on__year=year,
            reported_on__month=month
        ).count()
        
        crime_by_month.append({
            'month': f'{year}-{month:02d}',
            'count': count
        })
    
    crime_by_month.reverse()
    
    data = {
        'crime_by_category': crime_by_category,
        'crime_by_location': crime_by_location,
        'crime_by_status': crime_by_status,
        'crime_by_month': crime_by_month
    }
    
    return JsonResponse(data)