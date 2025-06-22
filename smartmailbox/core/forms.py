import re
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Device

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Podany adres email jest już zarejestrowany.")
        return email

class ActivationCodeForm(forms.Form):
    code = forms.CharField(label="Kod aktywacyjny", max_length=10)

    def clean_code(self):
        code = self.cleaned_data['code']
        if not re.fullmatch(r'[A-Z0-9]{6}', code):
            raise forms.ValidationError("Kod powinien składać się z 6 dużych liter lub cyfr.")
        return code

class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['device_id', 'security_code']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_device_id(self):
        device_id = self.cleaned_data.get('device_id')
        if self.user and device_id:
            if Device.objects.filter(owner=self.user, device_id=device_id).exists():
                raise forms.ValidationError("To urządzenie jest już zarejestrowane na Twoim koncie.")
        return device_id

class EmailChangeForm(forms.Form):
    current_email = forms.EmailField(
        label="Twój aktualny adres email", disabled=True
    )
    new_email = forms.EmailField(label="Nowy adres email")
    new_email_repeat = forms.EmailField(label="Powtórz nowy adres email")
    password = forms.CharField(label="Aktualne hasło", widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields['current_email'].initial = user.email

    def clean_new_email(self):
        new_email = self.cleaned_data.get('new_email')
        if new_email and new_email != self.user.email:
            if User.objects.filter(email=new_email).exclude(pk=self.user.pk).exists():
                raise forms.ValidationError("Ten adres email jest już zajęty przez innego użytkownika.")
        return new_email

    def clean(self):
        cleaned_data = super().clean()
        new_email = cleaned_data.get('new_email')
        new_email_repeat = cleaned_data.get('new_email_repeat')
        password = cleaned_data.get('password')

        if new_email and new_email_repeat and new_email != new_email_repeat:
            self.add_error('new_email_repeat', "Adresy email muszą być identyczne.")

        if password and not self.user.check_password(password):
            self.add_error('password', "Nieprawidłowe hasło.")

        if new_email == self.user.email:
            self.add_error('new_email', "Nowy adres email nie może być taki sam jak obecny.")

        return cleaned_data

class DeleteAccountForm(forms.Form):
    password = forms.CharField(label="Potwierdź hasło", widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_password(self):
        password = self.cleaned_data['password']
        if not self.user.check_password(password):
            raise forms.ValidationError("Nieprawidłowe hasło.")
        return password
