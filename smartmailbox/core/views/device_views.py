import json
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.timezone import is_naive, make_aware
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from core.decorators import activation_required
from core.utils.notifications import create_notification_and_email
from ..forms import DeviceForm
from ..models import Device, DeviceNotification


@login_required
@activation_required
def my_devices(request):
    return render(request, "my_devices.html")

@login_required
@activation_required
def devices_list(request):
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
            'display_battery': '--%' if status == "Niedostępne" else f"{device.battery_level}%",
            'detected_weight': '---' if status == "Niedostępne" else f"{device.detected_weight}",
            'status': status,
            'status_class': status_class,
        })

    html = render_to_string('devices_list.html', {'devices': device_list})
    return JsonResponse({'html': html})

    
@login_required
@activation_required
@require_POST
def ajax_delete_device(request):
    device_id = request.POST.get('device_id')
    device = Device.objects.filter(device_id=device_id, owner=request.user).first()
    if device:
        device.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Urządzenie nie istnieje'}, status=400)

@login_required
@activation_required
def add_device(request):
    if request.method == "POST":
        form = DeviceForm(request.POST, user=request.user)
        if form.is_valid():
            device = form.save(commit=False)
            device.owner = request.user
            device_count = Device.objects.filter(owner=request.user).count() + 1
            device.name = f"Urządzenie {device_count}"
            device.save()
            return redirect('my_devices')
    else:
        form = DeviceForm(user=request.user)
    return render(request, "add_device.html", {"form": form})


@login_required
@activation_required
@require_POST
def ajax_rename_device(request):
    device_id = request.POST.get('device_id')
    new_name = request.POST.get('new_name')
    device = Device.objects.filter(device_id=device_id, owner=request.user).first()
    if device and new_name:
        if Device.objects.filter(owner=request.user, name=new_name).exclude(id=device.id).exists():
            return JsonResponse({'success': False, 'error': 'Masz już urządzenie o tej nazwie!'}, status=400)
        device.name = new_name
        device.save()
        return JsonResponse({'success': True, 'new_name': new_name})
    return JsonResponse({'success': False, 'error': 'Nieprawidłowe dane'}, status=400)

@login_required
@activation_required
def notifications_table(request):
    notifications = DeviceNotification.objects.filter(
        device__owner=request.user
    ).order_by('-created_at')
    html = render_to_string('notifications_table.html', {'notifications': notifications})
    return JsonResponse({'html': html})

@login_required
@activation_required
@require_POST
def delete_notifications(request):
    ids = request.POST.getlist('notification_ids')
    if ids:
        DeviceNotification.objects.filter(id__in=ids, device__owner=request.user).delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'No IDs provided'}, status=400)



@csrf_exempt
def device_event_api(request):
    AUTH_TOKEN = getattr(settings, "IOT_AUTH_TOKEN", None)
    if request.headers.get('Authorization') != f'Token {AUTH_TOKEN}':
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    try:
        data = json.loads(request.body.decode())
        device_id = data.get('device_id')
        security_code = data.get('security_code')
        msg_type = data.get('msg_type')
        battery_level = data.get('battery_level')
        timestamp = data.get('timestamp')
        weight = data.get('weight', None)

        device = Device.objects.filter(device_id=device_id, security_code=security_code).first()
        if not device:
            return JsonResponse({'error': 'Device not found'}, status=404)

        previous_weight = getattr(device, 'detected_weight', 0) or 0

        if battery_level is not None:
            device.battery_level = battery_level
        if weight is not None:
            device.detected_weight = weight

        if msg_type == "HEARTBEAT":
            if timestamp:
                dt = parse_datetime(timestamp)
                if dt and is_naive(dt):
                    dt = make_aware(dt, timezone.get_current_timezone())
                device.last_heartbeat_time = dt or timezone.now()
            else:
                device.last_heartbeat_time = timezone.now()
        elif msg_type in ["MAIL_IN", "MAIL_OUT"]:
            handle_mail_event(device, msg_type, previous_weight, weight if weight is not None else previous_weight)
        elif msg_type == "LOW_BATTERY":
            handle_low_battery(device, battery_level)
        elif msg_type == "CONNECTION_LOST":
            handle_connection_lost(device)
        device.save()
        return JsonResponse({'success': True})

    except Exception as e:
        logging.exception("Błąd device_event_api")
        return JsonResponse({'error': f'Invalid request: {str(e)}'}, status=400)


def handle_mail_event(device, msg_type, previous_weight, new_weight):
    create_notification_and_email(device, msg_type, previous_weight, new_weight)

def handle_low_battery(device, battery_level):
    create_notification_and_email(device, 'LOW_BATTERY', extra_info={'battery_level': battery_level})

def handle_connection_lost(device):
    last_notification = DeviceNotification.objects.filter(device=device).order_by('-created_at').first()
    if not last_notification or last_notification.msg_type != "CONNECTION_LOST":
        create_notification_and_email(device, "CONNECTION_LOST")

