from django.db import models
import uuid
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    activated = models.BooleanField(default=False)
    activation_code = models.CharField(max_length=36, null=True, blank=True)
    activation_code_sent_at = models.DateTimeField(null=True, blank=True)  # do limitu resendu

    def generate_activation_code(self):
        code = str(uuid.uuid4()).replace('-', '')[:6].upper()  # np. 6 cyfr/znaków
        self.activation_code = code
        from django.utils import timezone
        self.activation_code_sent_at = timezone.now()
        self.save()
        return code

    def __str__(self):
        return f"Profil użytkownika {self.user.username}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

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
    registration_date = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    def __str__(self):
        return f"{self.device_id} (owner: {self.owner.username})"

class DeviceNotification(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    msg_type = models.CharField(max_length=20)
    previous_weight = models.FloatField()
    current_weight = models.FloatField()

    @property
    def weight_difference(self):
        return round(self.current_weight - self.previous_weight, 2)

    def __str__(self):
        return f"[{self.created_at}] {self.device.name}: {self.msg_type} ({self.weight_diff()} g)"

class UserNotificationSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    notify_mail_in = models.BooleanField(default=True)
    notify_mail_out = models.BooleanField(default=True)
    notify_low_battery = models.BooleanField(default=True)
    notify_lost_connection = models.BooleanField(default=True)

    def __str__(self):
        return f"Powiadomienia {self.user.username}"
