from django.conf import settings
from django.db import models

from dorm_system.common.models import Role


class UserProfile(models.Model):
    """Extends the Django auth user with role and phone, per the report."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    phone = models.CharField(max_length=20, blank=True, default="")

    def has_role(self, *roles):
        return self.role in roles

    def is_staff_role(self):
        return self.role in (Role.ADMIN, Role.FINANCE, Role.SYSADMIN)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


def get_profile(user):
    """Return the UserProfile for a user, creating a default if missing."""
    if user is None or not user.is_authenticated:
        return None
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile
