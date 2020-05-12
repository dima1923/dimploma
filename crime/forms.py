from django import forms
from django.contrib.auth.models import User

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta():
        model = User
        fields = ('first_name','last_name','username', 'password', 'email')
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'username': 'Логин',
            'password': 'Пароль',
            'email': 'Email'
        }
