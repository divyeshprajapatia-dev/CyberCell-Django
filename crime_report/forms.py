from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import CrimeReport, Location, UserProfile, CrimeUpdate

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('phone_number', 'address', 'profile_picture')
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            if profile_picture.size > 5 * 1024 * 1024:  # 5MB
                raise ValidationError('Profile picture size should not exceed 5MB.')
            valid_extensions = ['.jpg', '.jpeg', '.png']
            import os
            ext = os.path.splitext(profile_picture.name)[1].lower()
            if ext not in valid_extensions:
                raise ValidationError('Please upload a valid image file (jpg, jpeg, png).')
        return profile_picture

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('phone_number', 'address', 'profile_picture')
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ('city', 'state', 'area', 'pincode')
        widgets = {
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'area': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control', 'pattern': '[0-9]{6}', 'title': 'Enter a valid 6-digit pincode'}),
        }
    
    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode')
        if not pincode.isdigit() or len(pincode) != 6:
            raise ValidationError('Please enter a valid 6-digit pincode.')
        return pincode

class CrimeReportForm(forms.ModelForm):
    class Meta:
        model = CrimeReport
        fields = ('title', 'description', 'date_of_crime', 'time_of_crime', 'category', 'evidence_file')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'date_of_crime': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time_of_crime': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'evidence_file': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def clean_date_of_crime(self):
        date_of_crime = self.cleaned_data.get('date_of_crime')
        if date_of_crime > timezone.now().date():
            raise ValidationError('Date of crime cannot be in the future.')
        return date_of_crime
    
    def clean_evidence_file(self):
        evidence_file = self.cleaned_data.get('evidence_file')
        if evidence_file:
            if evidence_file.size > 5 * 1024 * 1024:  # 5MB
                raise ValidationError('Evidence file size should not exceed 5MB.')
            valid_extensions = ['.jpg', '.jpeg', '.png', '.pdf', '.doc', '.docx']
            import os
            ext = os.path.splitext(evidence_file.name)[1].lower()
            if ext not in valid_extensions:
                raise ValidationError('Please upload a valid file (jpg, jpeg, png, pdf, doc, docx).')
        return evidence_file

class CrimeUpdateForm(forms.ModelForm):
    class Meta:
        model = CrimeUpdate
        fields = ('update_text',)
        widgets = {
            'update_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean_update_text(self):
        update_text = self.cleaned_data.get('update_text')
        if len(update_text.strip()) < 10:
            raise ValidationError('Update text must be at least 10 characters long.')
        return update_text

class CrimeStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = CrimeReport
        fields = ('status', 'assigned_to')
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(
            profile__user_type__in=['police', 'admin']
        )
    
    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        assigned_to = cleaned_data.get('assigned_to')
        
        if status in ['investigating', 'resolved'] and not assigned_to:
            raise ValidationError({
                'assigned_to': 'An officer must be assigned for investigating or resolved cases.'
            })
        
        return cleaned_data

class UserTypeUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('user_type', 'police_id', 'department')
        widgets = {
            'user_type': forms.Select(attrs={'class': 'form-control'}),
            'police_id': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        police_id = cleaned_data.get('police_id')
        department = cleaned_data.get('department')
        
        if user_type == 'police':
            if not police_id:
                raise ValidationError({
                    'police_id': 'Police ID is required for police officers.'
                })
            if not department:
                raise ValidationError({
                    'department': 'Department is required for police officers.'
                })
        
        return cleaned_data