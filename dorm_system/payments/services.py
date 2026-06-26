"""PaymentReviewService (report Section 8.1).

Two-step payment flow: students submit evidence, finance confirms or rejects.
Only confirmed payments reduce the outstanding balance.
"""

from datetime import date

from django.core.mail import send_mail
from django.db import transaction

from dorm_system.billing.services import refresh_invoice_status
from dorm_system.common.models import (
    InvoiceStatus,
    NotificationChannel,
    NotificationStatus,
    PaymentStatus,
    record_audit,
)
from dorm_system.payments.models import Payment, PaymentEvidence


class PermissionDenied(Exception):
    pass


ALLOWED_EVIDENCE = (".jpg", ".jpeg", ".png", ".pdf")
MAX_EVIDENCE_BYTES = 5 * 1024 * 1024  # 5 MB per file


def _validate_file(f):
    name = (getattr(f, "name", "") or "").lower()
    if not name.endswith(ALLOWED_EVIDENCE):
        raise ValueError(f"Unsupported file type: {name}")
    if getattr(f, "size", 0) > MAX_EVIDENCE_BYTES:
        raise ValueError("File exceeds 5 MB limit.")
    return True


@transaction.atomic
def submit_payment_evidence(invoice, amount, files, student, *, source="student_portal"):
    """Create a pending payment with evidence (FR-09, FR-10)."""
    if invoice.student_id != student.id:
        raise PermissionDenied("Invoice does not belong to this student.")
    for f in files:
        _validate_file(f)

    payment = Payment.objects.create(
        invoice=invoice,
        student=student,
        amount=amount,
        status=PaymentStatus.PENDING_REVIEW,
        method="bank_transfer",
    )
    for f in files:
        PaymentEvidence.objects.create(payment=payment, file=f, source=source)
    return payment


def send_payment_review_digest():
    """Group pending submissions and email finance (report pseudocode).

    Uses the configured email backend (console in dev) and records a
    notification log entry per payment.
    """
    from dorm_system.communications.models import Notification
    from dorm_system.accounts.models import UserProfile
    from dorm_system.common.models import Role

    pending = list(
        Payment.objects.select_related("invoice", "student")
        .filter(status=PaymentStatus.PENDING_REVIEW, review_email_sent=False)
    )
    if not pending:
        return 0

    finance = UserProfile.objects.filter(role=Role.FINANCE).first()
    lines = []
    for payment in pending:
        lines.append(
            f"- {payment.invoice.invoice_number} | {payment.student.full_name} "
            f"| {payment.amount:,.0f} VND | {payment.invoice.due_date}"
        )
        if finance is not None:
            from dorm_system.communications.services import record_notification

            record_notification(
                finance.user,
                NotificationChannel.EMAIL,
                f"Payment review: {payment.invoice.invoice_number}",
                f"Payment {payment.id} awaits review.",
            )
        payment.review_email_sent = True
        payment.save(update_fields=["review_email_sent"])

    subject = f"Payment review digest: {len(pending)} payment(s) pending"
    body = "The following payments are awaiting finance review:\n\n" + "\n".join(lines)
    try:
        send_mail(
            subject,
            body,
            "dorm@example.edu",
            ["finance@example.edu"],
            fail_silently=True,
        )
    except Exception:
        pass
    return len(pending)


@transaction.atomic
def confirm_payment(payment, actor, note=""):
    """Finance confirms a payment; invoice status is recomputed (FR-10)."""
    payment = Payment.objects.select_for_update().get(pk=payment.pk)
    if payment.status != PaymentStatus.PENDING_REVIEW:
        raise PermissionDenied("Payment is not pending review.")
    payment.status = PaymentStatus.CONFIRMED
    payment.reviewed_by = actor
    payment.review_note = note
    payment.save(update_fields=["status", "reviewed_by", "review_note"])
    refresh_invoice_status(payment.invoice)
    record_audit(
        actor, "confirm_payment", "payment", payment.id,
        new_value={"status": payment.status, "invoice": payment.invoice.id},
        reason=note,
    )
    return payment


@transaction.atomic
def reject_payment(payment, actor, note=""):
    """Reject: balance is NOT reduced (NFR-02, FR-10)."""
    payment = Payment.objects.select_for_update().get(pk=payment.pk)
    if payment.status != PaymentStatus.PENDING_REVIEW:
        raise PermissionDenied("Payment is not pending review.")
    payment.status = PaymentStatus.REJECTED
    payment.reviewed_by = actor
    payment.review_note = note
    payment.save(update_fields=["status", "reviewed_by", "review_note"])
    refresh_invoice_status(payment.invoice)
    record_audit(
        actor, "reject_payment", "payment", payment.id,
        new_value={"status": payment.status}, reason=note,
    )
    return payment
