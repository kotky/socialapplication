from socialapp.models import User, SocialUser
from django.contrib.auth.forms import AuthenticationForm
from django import forms

class RegistrationFormUser(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ['username', 'password','email','first_name', 'last_name']
    def __init__(self, *args, **kwargs):
        super(RegistrationFormUser, self).__init__(*args, **kwargs)
        for value in self.fields.values():
            value.widget.attrs\
            .update({
                'class': 'form-control input-md'
            })


class RegistrationFormSocialUser(forms.ModelForm):
    class Meta:
        model = SocialUser
        fields = ('phone',)
    def __init__(self, *args, **kwargs):
        super(RegistrationFormSocialUser, self).__init__(*args, **kwargs)
        for value in self.fields.values():
            value.widget.attrs\
            .update({
                'class': 'form-control input-md'
            })


class LoginForm(AuthenticationForm):
    password = forms.CharField(widget=forms.PasswordInput())
    username = forms.CharField(widget=forms.TextInput())
    class Meta:
        model = User
        fields = ('username', 'password')
    def __init__(self, *args, **kwargs):
        super(AuthenticationForm, self).__init__(*args, **kwargs)
        for value in self.fields.values():
            value.widget.attrs\
            .update({
                'class': 'form-control input-md'
            })