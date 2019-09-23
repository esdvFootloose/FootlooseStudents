from django import forms

class Confirm(forms.Form):
    confirm = forms.BooleanField()