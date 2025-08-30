from django.contrib import admin
from .models import CrimeCategory, Location, CrimeReport, CrimeUpdate, UserProfile

@admin.register(CrimeCategory)
class CrimeCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('area', 'city', 'state', 'pincode')
    search_fields = ('area', 'city', 'state', 'pincode')
    list_filter = ('state', 'city')

@admin.register(CrimeReport)
class CrimeReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'location', 'reported_by', 'reported_on', 'status')
    list_filter = ('status', 'category', 'location__city', 'reported_on')
    search_fields = ('title', 'description', 'reported_by__username')
    date_hierarchy = 'reported_on'
    raw_id_fields = ('reported_by', 'assigned_to')

@admin.register(CrimeUpdate)
class CrimeUpdateAdmin(admin.ModelAdmin):
    list_display = ('crime_report', 'updated_by', 'updated_on')
    list_filter = ('updated_on',)
    search_fields = ('update_text', 'crime_report__title')
    date_hierarchy = 'updated_on'
    raw_id_fields = ('crime_report', 'updated_by')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'phone_number', 'department')
    list_filter = ('user_type', 'department')
    search_fields = ('user__username', 'user__email', 'phone_number', 'police_id')
    raw_id_fields = ('user',)
