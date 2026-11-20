from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.db import models


def avatar_path(instance, filename):
    return f'avatars/{uuid4().hex}{Path(filename).suffix.lower()}'


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, models.CASCADE, verbose_name='Пользователь'
    )
    avatar = models.ImageField('Аватар', upload_to=avatar_path, blank=True)

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return str(self.user)
