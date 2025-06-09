from django.shortcuts import render, redirect
from .forms import RegisterForm
from .forms import DeviceForm
from .models import Device
from django.contrib.auth.decorators import login_required

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})

@login_required
def my_devices(request):
    devices = Device.objects.filter(owner=request.user)
    return render(request, "my_devices.html", {"devices": devices})

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