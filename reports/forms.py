from django import forms
from .models import Report

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['issue_type', 'photo', 'location', 'description', 'contact_preference']
        widgets = {
            'issue_type': forms.Select(attrs={'class': 'form-select'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter location or address...'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Provide more details...'}),
            'contact_preference': forms.RadioSelect(attrs={'class': 'form-check-input'}),
        }
