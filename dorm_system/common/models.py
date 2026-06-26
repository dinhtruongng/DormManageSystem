"""Shared domain primitives and the audit log.

The common package holds cross-cutting types used by every feature app: status
enums, the audit trail model, and small helpers that should not depend on any
feature app (so the layering rule "models must not import views" is respected).
"""

from django.conf import settings
from django.db import models


class Role(models.TextChoices):
    """Role values stored on UserProfile; mirrored by Django auth Groups."""

    ADMIN = "admin", "Admin"
    FINANCE = "finance", "Finance"
    STUDENT = "student", "Student"
    SYSADMIN = "sysadmin", "System Admin"


class Gender(models.TextChoices):
    MALE = "male", "Male"
    FEMALE = "female", "Female"
    OTHER = "other", "Other"


class StudentStatus(models.TextChoices):
    APPLICANT = "applicant", "Applicant"
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    CHECKED_OUT = "checked_out", "Checked Out"
    SUSPENDED = "suspended", "Suspended"


class BuildingStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"


class RoomStatus(models.TextChoices):
    OPEN = "open", "Open"
    FULL = "full", "Full"
    MAINTENANCE = "maintenance", "Maintenance"
    INACTIVE = "inactive", "Inactive"


class GenderPolicy(models.TextChoices):
    MALE = "male", "Male only"
    FEMALE = "female", "Female only"
    MIXED = "mixed", "Mixed"
    UNSPECIFIED = "unspecified", "Unspecified"


class BedStatus(models.TextChoices):
    AVAILABLE = "available", "Available"
    RESERVED = "reserved", "Reserved"
    OCCUPIED = "occupied", "Occupied"
    CLEANING = "cleaning", "Cleaning / Maintenance"
    INACTIVE = "inactive", "Inactive"


class AssignmentStatus(models.TextChoices):
    RESERVED = "reserved", "Reserved"
    ACTIVE = "active", "Active"
    TRANSFERRED = "transferred", "Transferred"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Canceled"


class InspectionType(models.TextChoices):
    CHECKIN = "checkin", "Check-in"
    CHECKOUT = "checkout", "Check-out"
    FOLLOWUP = "followup", "Follow-up"


class InvoiceStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    ISSUED = "issued", "Issued"
    PARTIALLY_PAID = "partially_paid", "Partially Paid"
    PAID = "paid", "Paid"
    OVERDUE = "overdue", "Overdue"
    CANCELLED = "cancelled", "Canceled"


class InvoiceItemType(models.TextChoices):
    RENT = "rent", "Rent"
    DEPOSIT = "deposit", "Deposit"
    FEE = "fee", "Fee"
    PENALTY = "penalty", "Penalty"
    ADJUSTMENT = "adjustment", "Adjustment"


class PaymentMethod(models.TextChoices):
    BANK_TRANSFER = "bank_transfer", "Bank transfer"
    CASH = "cash", "Cash"
    CARD = "card", "Card"
    OTHER = "other", "Other"


class PaymentStatus(models.TextChoices):
    PENDING_REVIEW = "pending_review", "Pending Review"
    CONFIRMED = "confirmed", "Confirmed"
    REJECTED = "rejected", "Rejected"
    VOIDED = "voided", "Voided"


class Audience(models.TextChoices):
    ALL = "all", "Everyone"
    STUDENTS = "students", "Students"
    STAFF = "staff", "Staff"


class NotificationChannel(models.TextChoices):
    EMAIL = "email", "Email"
    IN_APP = "in_app", "In-app"


class NotificationStatus(models.TextChoices):
    QUEUED = "queued", "Queued"
    SENT = "sent", "Sent"
    FAILED = "failed", "Failed"
    READ = "read", "Read"


class AuditLog(models.Model):
    """Immutable decision trail for financial and occupancy state changes.

    Records actor, action, target reference, and a JSON snapshot of old/new
    values (report NFR-07). Write access is restricted to service helpers.
    """

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="audit_actions",
    )
    action = models.CharField(max_length=120)
    target_type = models.CharField(max_length=80)
    target_id = models.IntegerField(null=True, blank=True)
    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    reason = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["target_type", "target_id"])]

    def __str__(self):
        return f"{self.action} {self.target_type}:{self.target_id} by {self.actor}"


def record_audit(actor, action, target_type, target_id, old_value=None, new_value=None, reason=""):
    """Helper used by services to append an audit entry."""
    return AuditLog.objects.create(
        actor=actor,
        action=action,
        target_type=target_type,
        target_id=target_id,
        old_value=old_value,
        new_value=new_value,
        reason=reason,
    )
