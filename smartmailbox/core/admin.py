from django.contrib import admin
from .models import Device
from django.contrib.auth.models import User

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('device_id', 'name', 'owner', 'battery_level', 'last_package_time')
    list_filter = ('owner', 'battery_level')
    search_fields = ('device_id', 'name', 'owner__username')
    actions = ['reset_battery', 'set_name_to_default']

    @admin.action(description='Reset battery level to 100')
    def reset_battery(self, request, queryset):
        queryset.update(battery_level=100)

    @admin.action(description='Set name to "Urządzenie"')
    def set_name_to_default(self, request, queryset):
        queryset.update(name='Urządzenie')