from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, min_length=2)
    password = forms.CharField(max_length=100, min_length=4)