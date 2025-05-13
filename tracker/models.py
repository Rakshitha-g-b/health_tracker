from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class MoodEntry(models.Model):
    MOOD_CHOICES = [
        (1, 'Very Sad'),
        (2, 'Sad'),
        (3, 'Neutral'),
        (4, 'Happy'),
        (5, 'Very Happy'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    mood_level = models.IntegerField(choices=MOOD_CHOICES)
    notes = models.TextField(blank=True)
    ai_analysis = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.get_mood_level_display()} - {self.date.strftime('%Y-%m-%d %H:%M')}"

class HealthSymptom(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default='General Symptom')
    severity = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    notes = models.TextField(blank=True)
    date = models.DateTimeField(default=timezone.now)
    ai_analysis = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} - Severity: {self.severity}/10"

    class Meta:
        ordering = ['-date']

class DailyHabit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    sleep_hours = models.FloatField()
    water_intake_ml = models.IntegerField()
    exercise_minutes = models.IntegerField()
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s habits on {self.date.strftime('%Y-%m-%d')}"
