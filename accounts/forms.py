from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Player

class RegistrationForm(forms.Form):
    first_name = forms.CharField(label="First name", max_length=100)
    last_name = forms.CharField(label="Last name", max_length=100)
    email = forms.EmailField(label="Email", max_length=100)
    password1 = forms.CharField(label="Enter password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email):
            raise ValidationError("Someone already registered with that email")
        return email
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Password mismatch!")
        return password2

    def save(self):
        email = self.cleaned_data['email']
        password = self.cleaned_data['password1']
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
        user = User.objects.create_user(email, email, password, 
                                        first_name=first_name,
                                        last_name=last_name, player=Player())

class AssignmentForm(forms.Form):
    def __init__(self, *args, **kwargs): # to pass in the request object
        self.request = kwargs.pop('request', None)
        super(AssignmentForm, self).__init__(*args, **kwargs)

    target_code = forms.IntegerField(label="Target code")

    def clean_target_code(self):
        target_code = self.cleaned_data['target_code']
        if self.request.user.player.target.secret_code != target_code:
            raise forms.ValidationError("Code is invalid")
        return target_code


