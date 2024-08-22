from django import forms
from .models import Report, ReportObjective
from django.forms import modelformset_factory

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['title', 'audio_clips', 'author', 'date', 'report_objective']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'audio_clips': forms.CheckboxSelectMultiple(),
            'report_objective': forms.Select(),
        }
    

class ReportObjectiveForm(forms.ModelForm):
    class Meta:
        model = ReportObjective
        fields = ['sentence']
        widgets = {
            'sentence': forms.Textarea(attrs={'rows': 3}),
        }

