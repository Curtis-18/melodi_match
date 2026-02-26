from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Review, Genre

# Simplified form for reviews - just message field
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Share your thoughts about the genre prediction...',
                'class': 'form-control'
            })
        }

# Form for user sign-up
class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

# Form for user login
class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']