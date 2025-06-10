from django.db import models

from django.contrib.auth.models import User

class Device(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=50, unique=True)
    security_code = models.CharField(max_length=20)
    battery_level = models.IntegerField(default=100)
    last_package_time = models.DateTimeField(null=True, blank=True)
    name = models.CharField(max_length=100, default="Urządzenie")

    def __str__(self):
        return f"{self.device_id} (owner: {self.owner.username})"

# Create your models here.
