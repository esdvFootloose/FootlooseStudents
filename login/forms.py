from django import forms
from snowpenguin.django.recaptcha2.fields import ReCaptchaField
from snowpenguin.django.recaptcha2.widgets import ReCaptchaWidget

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, min_length=2)
    password = forms.CharField(max_length=100, min_length=4)
    # captcha = ReCaptchaField(widget=ReCaptchaWidget())