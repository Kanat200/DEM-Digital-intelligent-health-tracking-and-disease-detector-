# fit_app/models.py

from django.db import models
from django.contrib.auth.models import User


class FitData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    steps = models.IntegerField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.steps} steps on {self.date}"


class DataSource(models.Model):
    data_type = models.CharField(max_length=255)
    data_stream_id = models.CharField(max_length=255)


class DataPoint(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE, related_name='data_points')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    value = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.data_source.data_type} ({self.start_time} - {self.end_time}): {self.value}'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return self.user.username


class PredictHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return f'{self.user} - {self.created_at}: {self.value}'
