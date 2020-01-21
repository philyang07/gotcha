from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import *
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from ckeditor.widgets import CKEditorWidget
# from djrichtextfield.models import RichTextWidget
from .models import Player, Game
from tempus_dominus.widgets import DateTimePicker

from django.utils import timezone
import datetime

class PrettyPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(PrettyPasswordResetForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'   

class PrettyPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(PrettyPasswordChangeForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'  

class PrettySetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(PrettySetPasswordForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'  

class PrettyForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(PrettyForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class RegistrationForm(PrettyForm):
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['email'].help_text = "Your email is used for authentication purposes only and is erased upon completion of the game"

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

class CustomUserChangeForm(UserChangeForm):
    def __init__(self, *args, **kwargs): # to pass in the request object
        super(CustomUserChangeForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if "email" in self.changed_data and User.objects.filter(email=email):
            raise ValidationError("Someone already registered with that email")
        return email

    def clean(self):
        cleaned_data = super(CustomUserChangeForm, self).clean()
        first_name = cleaned_data['first_name']
        last_name = cleaned_data['last_name']        

        if ('first_name' in self.changed_data or 'last_name' in self.changed_data) and self.instance and self.instance.player:
            if [game for game in Game.objects.all() if self.instance.player in game.players()]: # if the user is a player in an actual game
                if self.instance.player.game.players().filter(user__first_name=first_name, user__last_name=last_name):
                    raise ValidationError("Someone in the same game already has the same name :(")
        
        return cleaned_data


class BareLoginForm(PrettyForm):
    """
        A login form I made for my own learning's sake
    """
    email = forms.EmailField(label="Email", max_length=100)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if not User.objects.filter(email=email):
            raise ValidationError("Email doesn't exist")
        elif User.objects.get(email=email).is_superuser:
            raise ValidationError("No superusers")
        return email

    def clean_password(self):
        email = self.cleaned_data.get('email')
        if not email:
            return
        password = self.cleaned_data['password']
        if not authenticate(username=email, password=password):
            raise ValidationError("Invalid password")
        return password

class PickyAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if user.is_superuser:
            raise forms.ValidationError("No superusers")

class AssignmentForm(PrettyForm):
    def __init__(self, *args, **kwargs): # to pass in the request object
        self.request = kwargs.pop('request', None)
        super(AssignmentForm, self).__init__(*args, **kwargs)
        self.fields['target_code'].help_text = "Once you complete an elimination, you must ask the target for their secret code"

    target_code = forms.IntegerField(label="Target code")

    def clean_target_code(self):
        target_code = self.cleaned_data['target_code']
        
        open_codes = [p.secret_code for p in self.request.user.player.game.open_players()]

        if (self.request.user.player.target.secret_code != target_code and target_code not in open_codes) or self.request.user.player.secret_code == target_code:
            raise forms.ValidationError("Code is invalid")
        return target_code

class ChangeGameDetailsForm(PrettyForm):
    def __init__(self, *args, **kwargs): # to pass in the request object
        self.request = kwargs.pop('request', None)
        super(ChangeGameDetailsForm, self).__init__(*args, **kwargs)   
        self.fields['open_duration'].help_text = "This is the timeframe in hours in which an elimination must be completed within before getting put on the open list"
        self.fields['access_code'].help_text = "Give this to new players so that they can join your game"
        self.fields['max_players'].help_text = "Limit to the number of players that can register for this game"
        self.fields['rules'].help_text = "Let the players know about any special rules e.g. safezones"
        if not self.request.user.game.in_registration:
            self.fields['target_assignment_time'].disabled = True
            self.fields['target_assignment_time'].help_text = "Already past registration"
        if not self.request.user.game.in_registration and not self.request.user.game.in_target_sending:
            self.fields['start_elimination_time'].disabled = True  
            self.fields['start_elimination_time'].help_text = "Already sent targets"  

    email = forms.EmailField(label="Email", max_length=100)
    access_code = forms.CharField(label="Access code", max_length=5, required=False)
    open_duration = forms.IntegerField(label="Open duration", required=True, min_value = 1, max_value=999)
    max_players = forms.IntegerField(label="Max no. of players", required=True, min_value=2, max_value=500)
    rules = forms.CharField(label="Rules", widget=CKEditorWidget(), max_length=1000, required=False)
    target_assignment_time = forms.DateTimeField(label='Target assignment time',         
        widget=DateTimePicker(
            options = {
                'format':  "MM/DD/YYYY HH:mm",
                'useCurrent': True,
                'collapse': False,
            },
            attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            }
        ), required=False)
    start_elimination_time = forms.DateTimeField(label='Start elimination time', 
        widget=DateTimePicker(
            options = {
                'format':  "MM/DD/YYYY HH:mm",
                'useCurrent': True,
                'collapse': False,
            },
            attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            }
        ), required=False)

    def clean_access_code(self):
        access_code = self.cleaned_data["access_code"].upper()
        if self.request.user.has_perm("accounts.game_admin"):
            if not access_code:
                raise ValidationError("Access code can't be blank")
            elif " " in access_code:
                raise ValidationError("Access code can't contain spaces")
            elif access_code != self.request.user.game.access_code and access_code in [g.access_code for g in Game.objects.all()]:
                raise ValidationError("Access code already exists")
        return access_code

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exclude(pk=self.request.user.pk):
            raise ValidationError("Someone already registered with that email")
        return email

    def clean(self):
        cleaned_data = super(ChangeGameDetailsForm, self).clean()

        if cleaned_data['start_elimination_time']: 
            if cleaned_data['target_assignment_time'] and cleaned_data['start_elimination_time'] < cleaned_data['target_assignment_time']:
                raise ValidationError("Elimination start time must be after target assignment time")
            elif cleaned_data['start_elimination_time'] <= timezone.now():
                raise ValidationError("Start elimination time must be after now!")

        if cleaned_data['target_assignment_time'] and cleaned_data['target_assignment_time'] <= timezone.now():
            raise ValidationError("Target assignment time must be after now!")

        return cleaned_data

class ChangePlayerDetailsForm(PrettyForm):
    def __init__(self, *args, **kwargs): # to pass in the request object
        self.request = kwargs.pop('request', None)
        super(ChangePlayerDetailsForm, self).__init__(*args, **kwargs)    
    
    first_name = forms.CharField(label="First name", max_length=100)
    last_name = forms.CharField(label="Last name", max_length=100)
    email = forms.EmailField(label="Email", max_length=100)
    death_message = forms.CharField(label="Death message", max_length=300, widget=forms.Textarea)

    def clean_first_name(self):
        first_name = self.cleaned_data["first_name"].lower().capitalize()
        if not first_name and not self.request.user.has_perm("accounts.game_admin"):
            raise ValidationError("First name can't be blank!")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data["last_name"].lower().capitalize()

        # trying to make sure names are unique
        first_name = self.cleaned_data["first_name"].lower().capitalize()
        game = Game.objects.filter(access_code=self.request.user.player.game.access_code)
        if game:
            game = game[0]
            if game.players().filter(user__first_name=first_name, user__last_name=last_name).exclude(pk=self.request.user.player.pk):
                raise ValidationError("Sorry, someone in the game has the same name! Change it slightly please :)")

        if not last_name and not self.request.user.has_perm("accounts.game_admin"):
            raise ValidationError("Last name can't be blank!")
        return last_name

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exclude(pk=self.request.user.pk):
            raise ValidationError("Someone already registered with that email")
        return email


class PlayerRegistrationForm(RegistrationForm):
    first_name = forms.CharField(label="First name", max_length=100)
    last_name = forms.CharField(label="Last name", max_length=100)
    access_code = forms.CharField(label="Game access code", max_length=10)

    def clean_access_code(self):
        access_code = self.cleaned_data["access_code"]
        if access_code not in [g.access_code for g in Game.objects.all()]:
            raise ValidationError("No game exists with that access code")
        return access_code

    def clean(self):
        cleaned_data = super(PlayerRegistrationForm, self).clean()

        last_name = cleaned_data["last_name"].lower().capitalize()
        if not cleaned_data.get("access_code"):
            return 
        access_code = cleaned_data["access_code"]
        first_name = cleaned_data["first_name"].lower().capitalize()
        game = Game.objects.filter(access_code=access_code)

        if game:
            game = game[0]
            if len(game.players()) >= game.max_players:
                raise ValidationError("Sorry, this game has reached its maximum number of players")

            if game.players().filter(user__first_name=first_name, user__last_name=last_name):
                raise ValidationError("Sorry, someone in the game has the same name! Change it slightly please :)")
        
        return cleaned_data


    



