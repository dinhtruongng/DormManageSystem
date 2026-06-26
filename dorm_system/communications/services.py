"""NotificationService (report Section 8.1).

Sends announcements and invoice reminders. In dev, email is the console
backend, so digests print to the runserver log.
"""

from django.core.mail import send_mail
from django.utils import timezone

from dorm_system.communications.models import Announcement, Notification
from dorm_system.common.models import NotificationChannel, NotificationStatus, Role


def send_announcement(announcement, recipients):
    """Fan out an announcement to a set of users and record notifications."""
    for user in recipients:
        Notification.objects.create(
            recipient=user,
            announcement=announcement,
            channel=NotificationChannel.EMAIL,
            subject=announcement.title,
            body=announcement.body,
            status=NotificationStatus.SENT,
        )
    announcement.published_at = timezone.now()
    announcement.save(update_fields=["published_at"])
    try:
        send_mail(
            announcement.title,
            announcement.body,
            "dorm@example.edu",
            [u.email for u in recipients if u.email],
            fail_silently=True,
        )
    except Exception:
        pass
    return announcement


def send_invoice_reminder(invoice):
    """Reminder for a single overdue/issued invoice."""
    if invoice.student.user is None or not invoice.student.user.email:
        return None
    subject = f"Reminder: invoice {invoice.invoice_number}"
    body = (
        f"Dear {invoice.student.full_name},\n\n"
        f"Your invoice {invoice.invoice_number} has an outstanding balance of "
        f"{invoice.balance_due():,.0f} VND due {invoice.due_date}.\n"
        "Please upload payment evidence in the student portal."
    )
    try:
        send_mail(subject, body, "dorm@example.edu", [invoice.student.user.email], fail_silently=True)
    except Exception:
        pass
    return Notification.objects.create(
        recipient=invoice.student.user,
        channel=NotificationChannel.EMAIL,
        subject=subject,
        body=body,
        status=NotificationStatus.SENT,
    )
