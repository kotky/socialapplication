from socialapp.models import User, SocialUser

from django import forms

class RegistrationFormUser(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ['username', 'password','email','first_name', 'last_name']

class RegistrationFormSocialUser(forms.ModelForm):
    class Meta:
        model = SocialUser
        fields = ('phone',)