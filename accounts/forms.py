from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

# Participant Signup
class ParticipantSignupForm(UserCreationForm):
    full_name = forms.CharField(max_length=100, required=True)
    roll_no = forms.IntegerField(required=True)
    admission_year = forms.IntegerField(required=True, help_text="e.g., 2023")
    mobile = forms.CharField(max_length=15, required=True)
    stream = forms.CharField(max_length=50, required=True, help_text="Enter stream like BCA, BBA(IB) etc.")
    
    class Meta:
        model = CustomUser
        fields = ['username', 'full_name', 'roll_no', 'admission_year', 'mobile', 'stream', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'participant'
        if commit:
            user.save()
        return user

# Event Manager Signup
class EventManagerSignupForm(UserCreationForm):
    full_name = forms.CharField(max_length=100, required=True)
    mobile = forms.CharField(max_length=15, required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'full_name', 'mobile', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'event_manager'
        if commit:
            user.save()
        return user
