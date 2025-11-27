from django import forms

class ExelUploadForm(forms.Form):
    excel_file = forms.FileField(label='Select an Excel file')