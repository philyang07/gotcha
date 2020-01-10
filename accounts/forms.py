from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Player, Game

class RegistrationForm(forms.Form):
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

class AssignmentForm(forms.Form):
    def __init__(self, *args, **kwargs): # to pass in the request object
        self.request = kwargs.pop('request', None)
        super(AssignmentForm, self).__init__(*args, **kwargs)

    target_code = forms.IntegerField(label="Target code")

    def clean_target_code(self):
        target_code = self.cleaned_data['target_code']
        
        open_codes = [p.secret_code for p in self.request.user.player.game.open_players()]
    
        if self.request.user.player.target.secret_code != target_code and target_code not in open_codes:
            raise forms.ValidationError("Code is invalid")
        return target_code

class PlayerRegistrationForm(RegistrationForm):
    first_name = forms.CharField(label="First name", max_length=100)
    last_name = forms.CharField(label="Last name", max_length=100)
    access_code = forms.CharField(label="Game access code", max_length=10)

    def clean_access_code(self):
        access_code = self.cleaned_data["access_code"]
        if access_code not in [g.access_code for g in Game.objects.all()]:
            raise ValidationError("No game exists with that access code")
        return access_code
    
# class GameCreationForm(RegistrationForm):
    



