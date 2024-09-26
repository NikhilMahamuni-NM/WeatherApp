from django.db import models

# Create your models here.

class WeatherDetails(models.Model):
    city = models.CharField(max_length=255, unique=True)
    timestamp = models.DateTimeField(auto_now=True)
    weather_details = models.JSONField()
    forecast_details = models.JSONField()
    previous_details = models.JSONField(null=True)

