from django.contrib.auth.models import AbstractUser
from django.db import models
from django_extensions.db.models import TimeStampedModel


class User(AbstractUser, TimeStampedModel):
    user_id = models.AutoField(primary_key=True)
    nickname = models.CharField(max_length=50)
    is_agree_ads = models.BooleanField(default=False)
    is_agree_privacy = models.BooleanField(default=False)
    email = models.EmailField(max_length=254, unique=True)

    def __str__(self):
        return self.username


class RefreshToken(TimeStampedModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="refresh_tokens",
    )
    token_hash = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)
