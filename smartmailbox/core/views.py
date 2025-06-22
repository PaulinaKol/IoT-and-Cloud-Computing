from django.shortcuts import render, redirect
from .forms import RegisterForm
from .forms import DeviceForm
from .models import Device, DeviceNotification, UserNotificationSettings, UserProfile
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.utils import timezone
from django.views.decorators.http import require_POST, require_GET
from django.template.loader import render_to_string
from django.http import JsonResponse
from .models import UserNotificationSettings
from core.utils.notifications import create_notification_and_email
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware, is_naive
from django.shortcuts import render, redirect
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import EmailChangeForm
from .forms import DeleteAccountForm
from django.contrib.auth import logout
from core.utils.notifications import send_activation_email
from .forms import ActivationCodeForm
from django.shortcuts import render, redirect
from django.contrib import messages
from core.decorators import activation_required
from django.contrib.auth import login


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_activation_email(user)  # WYŚLIJ kod aktywacyjny na email
            # (Opcjonalnie możesz automatycznie zalogować użytkownika)
            login(request, user)
            return redirect('activate_account')
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})


class CustomLoginView(LoginView):
    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user

        # Upewnij się, że UserProfile istnieje:
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'activated': False}
        )

        if not profile.activated:
            return redirect('activate_account')
        return response

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
                    create_notification_and_email(
                        device,
                        'LOW_BATTERY',
                        extra_info={'battery_level': device.battery_level}
                    )
            else:
                status = "Niedostępne"
                status_class = "status-unavailable"
                create_notification_and_email(
                    device,
                    'CONNECTION_LOST'
                )
        else:
            status = "Niedostępne"
            status_class = "status-unavailable"
            create_notification_and_email(
                device,
                'CONNECTION_LOST'
            )
        device_list.append({
            'name': device.name,
            'device_id': device.device_id,
            'security_code': device.security_code,
            'battery_level': device.battery_level,
            'display_battery': '--%' if status == "Niedostępne" else f"{device.battery_level}%",
            'detected_weight': '---' if status == "Niedostępne" else f"{device.detected_weight}%",
            'status': status,
            'status_class': status_class,
        })

    html = render_to_string('devices_list.html', {'devices': device_list})
    return JsonResponse({'html': html})

def home_redirect(request):
    if request.user.is_authenticated:
        return redirect('my_devices')
    else:
        return redirect('login')
    
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
        # Sprawdź, czy user już ma urządzenie o tej nazwie (ale z innym ID)
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

@login_required
@activation_required
def user_settings(request):
    # Na razie tylko placeholdery, później będą tu ustawienia pobierane z bazy
    return render(request, "user_settings.html")

@login_required
@activation_required
@require_GET
def ajax_get_user_notification_settings(request):
    settings, _ = UserNotificationSettings.objects.get_or_create(user=request.user)
    return JsonResponse({
        'notify_mail_in': settings.notify_mail_in,
        'notify_mail_out': settings.notify_mail_out,
        'notify_low_battery': settings.notify_low_battery,
        'notify_lost_connection': settings.notify_lost_connection,
    })

@login_required
@activation_required
@require_POST
def ajax_set_user_notification_settings(request):
    settings, _ = UserNotificationSettings.objects.get_or_create(user=request.user)
    settings.notify_mail_in = request.POST.get('notify_mail_in') == 'true'
    settings.notify_mail_out = request.POST.get('notify_mail_out') == 'true'
    settings.notify_low_battery = request.POST.get('notify_low_battery') == 'true'
    settings.notify_lost_connection = request.POST.get('notify_lost_connection') == 'true'
    settings.save()
    return JsonResponse({'success': True})

@csrf_exempt
def device_event_api(request):
    AUTH_TOKEN = "TEMP_TEST_TOKEN"
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
        
        # ZNAJDŹ URZĄDZENIE
        device = Device.objects.filter(device_id=device_id, security_code=security_code).first()
        if not device:
            return JsonResponse({'error': 'Device not found'}, status=404)
        
        # AKTUALIZUJ STATUSY I ZAPISZ POWIADOMIENIA
        previous_weight = getattr(device, 'detected_weight', 0) or 0
        if battery_level is not None:
            device.battery_level = battery_level
        if weight is not None:
            device.detected_weight = weight
        
        if msg_type == "HEARTBEAT":
            if timestamp:
                dt = parse_datetime(timestamp)
                if dt and is_naive(dt):
                    from django.utils import timezone
                    dt = make_aware(dt, timezone.get_current_timezone())
                if dt:
                    device.last_heartbeat_time = dt
                else:
                    device.last_heartbeat_time = timezone.now()
            else:
                device.last_heartbeat_time = timezone.now()
        if msg_type in ["MAIL_IN", "MAIL_OUT"]:
            create_notification_and_email(
                device,
                msg_type,
                previous_weight,
                weight if weight is not None else previous_weight
            )
        elif msg_type == "LOW_BATTERY":
            create_notification_and_email(
                device,
                msg_type,
                extra_info={'battery_level': battery_level}
            )
        elif msg_type == "CONNECTION_LOST":
            last_notification = DeviceNotification.objects.filter(device=device).order_by('-created_at').first()
            if not last_notification or last_notification.msg_type != "CONNECTION_LOST":
                create_notification_and_email(
                    device,
                    msg_type
            )
        device.save()

        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'error': f'Invalid request: {e}'}, status=400)

@login_required
@activation_required
def change_password(request):
    password_change_status = ""
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            password_change_status = "success"
            form = PasswordChangeForm(user=request.user)
        else:
            password_change_status = "error"
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'change_password.html', {
        'form': form,
        'password_change_status': password_change_status,
    })

@login_required
@activation_required
def change_email(request):
    email_change_status = ""
    if request.method == "POST":
        form = EmailChangeForm(request.user, request.POST)
        if form.is_valid():
            new_email = form.cleaned_data["new_email"]
            user = request.user
            user.email = new_email
            user.save()
            email_change_status = "success"
            form = EmailChangeForm(user)
        else:
            email_change_status = "error"
    else:
        form = EmailChangeForm(request.user)
    return render(request, "change_email.html", {
        "form": form,
        "email_change_status": email_change_status
    })

@login_required
@activation_required
def delete_account(request):
    delete_status = ""
    if request.method == "POST":
        form = DeleteAccountForm(request.user, request.POST)
        if form.is_valid():
            user = request.user
            logout(request)  # Wyloguj użytkownika przed usunięciem
            user.delete()    # Usuwa również powiązane urządzenia przez CASCADE
            delete_status = "success"
            # Po sukcesie od razu przejdź do szablonu końcowego
            return render(request, "delete_account_done.html")
        else:
            delete_status = "error"
    else:
        form = DeleteAccountForm(request.user)
    return render(request, "delete_account.html", {
        "form": form,
        "delete_status": delete_status
    })


def activate_account(request):
    user = request.user
    profile = user.userprofile
    form = ActivationCodeForm(request.POST or None)
    show_info = False

    # Dodaj flagę do sesji – kod wyślemy tylko przy pierwszym wejściu
    if not profile.activated:
        if not request.session.get('activation_email_sent', False):
            send_activation_email(user)
            request.session['activation_email_sent'] = True
            show_info = True

    # Obsługa ponownego wysłania kodu
    if 'resend' in request.GET:
        send_activation_email(user)
        show_info = True

    if request.method == 'POST' and form.is_valid():
        if form.cleaned_data['code'].strip().upper() == profile.activation_code:
            profile.activated = True
            profile.activation_code = ''
            profile.save()
            request.session.pop('activation_email_sent', None)  # usuń flagę z sesji
            messages.success(request, "Konto aktywowane. Możesz się już zalogować.")
            return redirect('login')
        else:
            messages.error(request, "Nieprawidłowy kod aktywacyjny.")

    return render(request, "activate_account.html", {
        'form': form,
        'user_email': user.email,
        'show_info': show_info,
    })