from django import forms
from django.forms import ValidationError

class XlsxUpload(forms.Form):
    file = forms.FileField()

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if not file:
            raise ValidationError("No file supplied!")
        if file.content_type != 'application/vnd.ms-excel' and file.content_type != "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            raise ValidationError("Not an excell file!")

class Confirm(forms.Form):
    confirm = forms.BooleanField()