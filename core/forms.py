from pathlib import Path

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UsernameField
from django.contrib.auth.models import User
from django.db import transaction

from .models import Profile


class LoginForm(AuthenticationForm):
    username = UsernameField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'id': 'login', 'placeholder': 'Enter your login here',
        }),
    )
    password = forms.CharField(
        strip=False, max_length=128,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'password'}),
    )


class AvatarField(forms.ImageField):
    def __init__(self):
        super().__init__(
            required=False,
            widget=forms.FileInput(attrs={
                'class': 'form-control', 'id': 'avatar', 'accept': '.jpg,.jpeg,.png',
            }),
        )

    def clean(self, data, initial=None):
        if data and data.size > 2 * 1024 * 1024:
            raise forms.ValidationError('Файл должен быть не больше 2 МБ.')
        image = super().clean(data, initial)
        if data:
            formats = {'.jpg': 'JPEG', '.jpeg': 'JPEG', '.png': 'PNG'}
            if formats.get(Path(data.name).suffix.lower()) != image.image.format:
                raise forms.ValidationError('Загрузите файл JPG или PNG.')
        return image


class ProfileForm(forms.ModelForm):
    username = UsernameField(
        min_length=3, max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'login'}),
    )
    email = forms.EmailField(
        max_length=254, widget=forms.EmailInput(attrs={'class': 'form-control', 'id': 'email'}),
    )
    first_name = forms.CharField(
        max_length=40, widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'nickname'}),
    )
    avatar = AvatarField()

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name')

    @transaction.atomic
    def save(self):
        user = super().save()
        profile, _ = Profile.objects.get_or_create(user=user)
        if self.cleaned_data['avatar']:
            profile.avatar = self.cleaned_data['avatar']
            profile.save()
        return user


class SignupForm(UserCreationForm):
    username = ProfileForm.base_fields['username']
    email = ProfileForm.base_fields['email']
    first_name = ProfileForm.base_fields['first_name']
    avatar = AvatarField()
    password1 = forms.CharField(
        strip=False, max_length=128,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'password'}),
    )
    password2 = forms.CharField(
        strip=False, max_length=128,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'password2'}),
    )

    class Meta(UserCreationForm.Meta):
        fields = ProfileForm.Meta.fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.pop('autofocus', None)

    @transaction.atomic
    def save(self):
        user = super().save()
        Profile.objects.create(user=user, avatar=self.cleaned_data['avatar'])
        return user
