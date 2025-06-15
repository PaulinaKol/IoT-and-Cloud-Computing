from django.shortcuts import render, redirect
from .forms import RegisterForm
from .forms import DeviceForm
from .models import Device, DeviceNotification
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})

from django.utils import timezone

@login_required
def my_devices(request):
    devices = Device.objects.filter(owner=request.user)
    now = timezone.now()
    device_list = []

    for device in devices:
        if device.last_heartbeat_time:
            delta = (now - device.last_heartbeat_time).total_seconds()
            if delta <= 15:
                if device.battery_level > 25:
                    status = "Dostępne"
                    status_class = "status-available"
                else:
                    status = "Niski Poziom Baterii"
                    status_class = "status-low-battery"
            else:
                status = "Niedostępne"
                status_class = "status-unavailable"
        else:
            status = "Niedostępne"
            status_class = "status-unavailable"

        device_list.append({
            'name': device.name,
            'device_id': device.device_id,
            'security_code': device.security_code,
            'battery_level': device.battery_level,
            'detected_weight': device.detected_weight,
            'status': status,
            'status_class': status_class,
        })

    notifications = DeviceNotification.objects.filter(
        device__owner=request.user
    ).order_by('-created_at')

    return render(request, "my_devices.html", {
        "devices": device_list,
        "notifications": notifications,
    })


@login_required
def add_device(request):
    if request.method == "POST":
        form = DeviceForm(request.POST)
        if form.is_valid():
            device = form.save(commit=False)
            device.owner = request.user
            device.save()
            return redirect('my_devices')
    else:
        form = DeviceForm()
    return render(request, "add_device.html", {"form": form})

def home_redirect(request):
    if request.user.is_authenticated:
        return redirect('my_devices')
    else:
        return redirect('login')
    
@login_required
def delete_device(request, device_id):
    device = get_object_or_404(Device, device_id=device_id, owner=request.user)
    if request.method == "POST":
        device.delete()
        return redirect('my_devices')
    return render(request, "delete_device_confirm.html", {"device": device})

@login_required
def add_device(request):
    if request.method == "POST":
        form = DeviceForm(request.POST)
        if form.is_valid():
            device = form.save(commit=False)
            device.owner = request.user
            # Liczba urządzeń użytkownika + 1, do domyślnej nazwy
            device_count = Device.objects.filter(owner=request.user).count() + 1
            device.name = f"Urządzenie {device_count}"
            device.save()
            return redirect('my_devices')
    else:
        form = DeviceForm()
    return render(request, "add_device.html", {"form": form})

from django.views.decorators.csrf import csrf_exempt  # lub użyj csrf_token w formularzu JS


@login_required
def rename_device(request):
    if request.method == "POST":
        device_id = request.POST.get('device_id')
        new_name = request.POST.get('new_name')
        device = Device.objects.filter(device_id=device_id, owner=request.user).first()
        if device and new_name:
            device.name = new_name
            device.save()
    return redirect('my_devices')

@login_required
@require_POST
def delete_notifications(request):
    ids = request.POST.getlist('notification_ids')
    if ids:
        DeviceNotification.objects.filter(id__in=ids, device__owner=request.user).delete()
    return redirect('my_devices')