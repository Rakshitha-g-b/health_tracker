from django import forms
from .models import MoodEntry, HealthSymptom, DailyHabit

class MoodEntryForm(forms.ModelForm):
    class Meta:
        model = MoodEntry
        fields = ['mood_level', 'notes']
        widgets = {
            'mood_level': forms.RadioSelect(),
            'notes': forms.Textarea(attrs={'rows': 4, 'placeholder': 'How are you feeling today? What made you feel this way?'})
        }
        labels = {
            'mood_level': 'How are you feeling?',
            'notes': 'Notes (optional)'
        }
        help_texts = {
            'mood_level': '1 = Very Sad, 2 = Sad, 3 = Neutral, 4 = Happy, 5 = Very Happy'
        }

class HealthSymptomForm(forms.ModelForm):
    class Meta:
        model = HealthSymptom
        fields = ['name', 'severity', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'severity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '10'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        labels = {
            'name': 'Symptom Name',
            'severity': 'Severity (1-10)',
            'notes': 'Additional Notes'
        }
        help_texts = {
            'severity': 'Rate from 1 (mild) to 10 (severe)',
            'notes': 'Describe your symptoms in detail for better AI analysis'
        }

class DailyHabitForm(forms.ModelForm):
    class Meta:
        model = DailyHabit
        fields = ['sleep_hours', 'water_intake_ml', 'exercise_minutes', 'notes']
        widgets = {
            'sleep_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '24',
                'step': '0.5',
                'placeholder': 'Enter hours (0-24)'
            }),
            'water_intake_ml': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '10000',
                'step': '100',
                'placeholder': 'Enter milliliters (0-10000)'
            }),
            'exercise_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '1440',
                'placeholder': 'Enter minutes (0-1440)'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '3',
                'placeholder': 'Add any additional notes about your daily habits'
            })
        }
        labels = {
            'sleep_hours': 'Sleep Hours',
            'water_intake_ml': 'Water Intake (ml)',
            'exercise_minutes': 'Exercise Minutes',
            'notes': 'Notes'
        }
    
    def clean_sleep_hours(self):
        sleep_hours = self.cleaned_data.get('sleep_hours')
        if sleep_hours is not None and (sleep_hours < 0 or sleep_hours > 24):
            raise forms.ValidationError("Sleep hours must be between 0 and 24")
        return sleep_hours
    
    def clean_water_intake_ml(self):
        water_intake = self.cleaned_data.get('water_intake_ml')
        if water_intake is not None and (water_intake < 0 or water_intake > 10000):
            raise forms.ValidationError("Water intake must be between 0 and 10000 ml")
        return water_intake
    
    def clean_exercise_minutes(self):
        exercise = self.cleaned_data.get('exercise_minutes')
        if exercise is not None and (exercise < 0 or exercise > 1440):
            raise forms.ValidationError("Exercise minutes must be between 0 and 1440")
        return exercise 