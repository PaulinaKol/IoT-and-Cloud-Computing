from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET, require_POST

from core.decorators import activation_required
from core.utils.notifications import send_activation_email
from ..forms import ActivationCodeForm, DeleteAccountForm, EmailChangeForm, RegisterForm
from ..models import UserProfile, UserNotificationSettings


def home_redirect(request):
    if request.user.is_authenticated:
        return redirect('my_devices')
    else:
        return redirect('login')

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_activation_email(user)
            login(request, user)
            return redirect('activate_account')
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})


class CustomLoginView(LoginView):
    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user

        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'activated': False}
        )

        if not profile.activated:
            return HttpResponseRedirect('/activate_account/')
        return response
    
@login_required
@activation_required
def user_settings(request):
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
    mapping = {
        'notify_mail_in': 'notify_mail_in',
        'notify_mail_out': 'notify_mail_out',
        'notify_low_battery': 'notify_low_battery',
        'notify_lost_connection': 'notify_lost_connection',
    }

    for key, field in mapping.items():
        val = request.POST.get(key)
        if val is None:
            continue
        if val.lower() not in ['true', 'false']:
            return JsonResponse({'success': False, 'error': f'Nieprawidłowa wartość dla {key}'}, status=400)
        setattr(settings, field, val.lower() == 'true')

    settings.save()
    return JsonResponse({'success': True})


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
            logout(request)
            user.delete()
            delete_status = "success"
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

    if not profile.activated:
        if not request.session.get('activation_email_sent', False):
            send_activation_email(user)
            request.session['activation_email_sent'] = True
            show_info = True

    if 'resend' in request.GET:
        send_activation_email(user)
        show_info = True

    if request.method == 'POST' and form.is_valid():
        if form.cleaned_data['code'].strip().upper() == profile.activation_code:
            profile.activated = True
            profile.activation_code = ''
            profile.save()
            request.session.pop('activation_email_sent', None)
            messages.success(request, "Konto aktywowane. Możesz się już zalogować.")
            return redirect('login')
        else:
            messages.error(request, "Nieprawidłowy kod aktywacyjny.")

    return render(request, "activate_account.html", {
        'form': form,
        'user_email': user.email,
        'show_info': show_info,
    })