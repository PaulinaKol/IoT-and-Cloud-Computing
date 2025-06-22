from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Device

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class ActivationCodeForm(forms.Form):
    code = forms.CharField(label="Kod aktywacyjny", max_length=10)

class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['device_id', 'security_code']  # lub inne pola do wpisania przez usera

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Przekaż usera do formularza!
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        device_id = cleaned_data.get('device_id')
        if self.user and device_id:
            if Device.objects.filter(owner=self.user, device_id=device_id).exists():
                raise forms.ValidationError("To urządzenie jest już zarejestrowane na Twoim koncie.")
        return cleaned_data

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


