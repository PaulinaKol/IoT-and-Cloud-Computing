from django.db import models

from django.contrib.auth.models import User

class Device(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=50, unique=True)
    security_code = models.CharField(max_length=20)
    battery_level = models.IntegerField(default=0)
    detected_weight = models.FloatField(default=0)
    last_heartbeat_time = models.DateTimeField(null=True, blank=True)
    name = models.CharField(max_length=100, default="Urządzenie")
    last_low_battery_email = models.DateTimeField(null=True, blank=True)
    last_connection_lost_email = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.device_id} (owner: {self.owner.username})"

class DeviceNotification(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    msg_type = models.CharField(max_length=20)  # 'MAIL_IN' lub 'MAIL_OUT'
    previous_weight = models.FloatField()
    current_weight = models.FloatField()

    @property
    def weight_difference(self):
        # Wynik zaokrąglony do dwóch miejsc po przecinku
        return round(self.current_weight - self.previous_weight, 2)

    def __str__(self):
        return f"[{self.created_at}] {self.device.name}: {self.msg_type} ({self.weight_diff()} g)"

class UserNotificationSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    notify_mail_in = models.BooleanField(default=True)
    notify_mail_out = models.BooleanField(default=False)
    notify_low_battery = models.BooleanField(default=True)
    notify_lost_connection = models.BooleanField(default=False)

    def __str__(self):
        return f"Powiadomienia {self.user.username}"
