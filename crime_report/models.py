from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from .validators import validate_file_extension, validate_file_size, validate_file_content

class CrimeCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Crime Categories"
        ordering = ['name']

class Location(models.Model):
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    pincode = models.CharField(
        max_length=10,
        validators=[RegexValidator(
            regex=r'^\d{6}$',
            message='Pincode must be 6 digits'
        )]
    )
    
    def __str__(self):
        return f"{self.area}, {self.city}, {self.state} - {self.pincode}"
    
    class Meta:
        ordering = ['state', 'city', 'area']
        unique_together = ['city', 'state', 'area', 'pincode']

class CrimeReport(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('investigating', 'Under Investigation'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    date_of_crime = models.DateField()
    time_of_crime = models.TimeField(null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    category = models.ForeignKey(CrimeCategory, on_delete=models.CASCADE)
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_crimes')
    reported_on = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    evidence_file = models.FileField(
        upload_to='evidence/',
        null=True,
        blank=True,
        validators=[validate_file_extension, validate_file_size, validate_file_content]
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_crimes',
        limit_choices_to={'profile__user_type__in': ['police', 'admin']}
    )
    
    def __str__(self):
        return self.title
    
    def clean(self):
        # Validate date_of_crime is not in future
        if self.date_of_crime and self.date_of_crime > timezone.now().date():
            raise ValidationError({'date_of_crime': 'Date of crime cannot be in the future'})
        
        # Validate assigned_to is police or admin
        if self.assigned_to and not self.assigned_to.profile.user_type in ['police', 'admin']:
            raise ValidationError({'assigned_to': 'Case can only be assigned to police officers or admins'})
    
    def get_status_display_class(self):
        """Returns Bootstrap class for status display"""
        status_classes = {
            'pending': 'warning',
            'investigating': 'info',
            'resolved': 'success',
            'closed': 'secondary'
        }
        return status_classes.get(self.status, 'primary')
    
    def can_update_status(self, user):
        """Check if user can update the status"""
        return user.profile.user_type in ['police', 'admin']
    
    def can_view_details(self, user):
        """Check if user can view full details"""
        return (user == self.reported_by or 
                user == self.assigned_to or 
                user.profile.user_type in ['police', 'admin'])
    
    class Meta:
        ordering = ['-reported_on']
        permissions = [
            ("can_assign_cases", "Can assign cases to officers"),
            ("can_update_status", "Can update case status"),
            ("can_view_all_cases", "Can view all cases"),
        ]

class CrimeUpdate(models.Model):
    crime_report = models.ForeignKey(CrimeReport, on_delete=models.CASCADE, related_name='updates')
    update_text = models.TextField()
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    updated_on = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Update on {self.crime_report.title} at {self.updated_on}"
    
    def clean(self):
        # Skip validation if updated_by is not set yet
        if not self.updated_by_id:
            return
        
        # Validate that updater is police or admin
        if not self.updated_by.profile.user_type in ['police', 'admin']:
            raise ValidationError('Only police officers and admins can add updates')
    
    class Meta:
        ordering = ['-updated_on']

class UserProfile(models.Model):
    USER_TYPES = (
        ('citizen', 'Citizen'),
        ('police', 'Police Officer'),
        ('admin', 'Admin'),
    )
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='citizen')
    police_id = models.CharField(max_length=50, blank=True, null=True, unique=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True,
        validators=[validate_file_extension, validate_file_size, validate_file_content]
    )
    
    def __str__(self):
        return f"{self.user.username} - {self.get_user_type_display()}"
    
    def clean(self):
        # Validate police_id and department for police officers
        if self.user_type == 'police':
            if not self.police_id:
                raise ValidationError({'police_id': 'Police ID is required for police officers'})
            if not self.department:
                raise ValidationError({'department': 'Department is required for police officers'})
        
        # Clear police_id and department for non-police users
        if self.user_type != 'police':
            self.police_id = None
            self.department = None
    
    def is_police_or_admin(self):
        return self.user_type in ['police', 'admin']
    
    def can_manage_users(self):
        return self.user_type == 'admin'
    
    class Meta:
        ordering = ['-user_type', 'user__username']