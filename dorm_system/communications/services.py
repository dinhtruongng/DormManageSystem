"""NotificationService (report Section 8.1).

Sends announcements and invoice reminders. In dev, email is the console
backend, so digests print to the runserver log.
"""

from django.core.mail import send_mail
from django.utils import timezone

from dorm_system.communications.models import Announcement, Notification
from dorm_system.common.models import NotificationChannel, NotificationStatus, Role


def record_notification(recipient, channel, subject, body="", *, status=NotificationStatus.SENT, announcement=None):
    """Persist a single notification log entry (§9.8 NotificationService).

    Centralizes Notification creation so announcement/reminder/digest flows
    share one write path and a consistent default status.
    """
    return Notification.objects.create(
        recipient=recipient,
        announcement=announcement,
        channel=channel,
        subject=subject,
        body=body,
        status=status,
    )


def send_announcement(announcement, recipients):
    """Fan out an announcement to a set of users and record notifications."""
    for user in recipients:
        record_notification(
            user,
            NotificationChannel.EMAIL,
            announcement.title,
            announcement.body,
            announcement=announcement,
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
    return record_notification(
        invoice.student.user,
        NotificationChannel.EMAIL,
        subject,
        body,
    )
