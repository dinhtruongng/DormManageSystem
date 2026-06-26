from django.conf import settings
from django.db import models

from dorm_system.common.models import Audience, NotificationChannel, NotificationStatus


class Announcement(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    audience = models.CharField(
        max_length=16, choices=Audience.choices, default=Audience.ALL
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="announcements",
    )
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    announcement = models.ForeignKey(
        Announcement,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
    )
    channel = models.CharField(
        max_length=12, choices=NotificationChannel.choices, default=NotificationChannel.EMAIL
    )
    subject = models.CharField(max_length=200)
    body = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=12, choices=NotificationStatus.choices, default=NotificationStatus.QUEUED
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["status"])]

    def __str__(self):
        return f"{self.subject} -> {self.recipient}"
