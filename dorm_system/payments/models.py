from django.conf import settings
from django.db import models

from dorm_system.billing.models import Invoice
from dorm_system.common.models import PaymentMethod, PaymentStatus
from dorm_system.residents.models import Student


class PaymentManager(models.Manager):
    def pending_review(self):
        return self.filter(status=PaymentStatus.PENDING_REVIEW)


class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name="payments")
    student = models.ForeignKey(
        Student, on_delete=models.PROTECT, related_name="payments"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(
        max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.BANK_TRANSFER
    )
    status = models.CharField(
        max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING_REVIEW
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments_reviewed",
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    review_email_sent = models.BooleanField(default=False)
    review_note = models.CharField(max_length=255, blank=True, default="")

    objects = PaymentManager()

    class Meta:
        ordering = ["-submitted_at"]
        indexes = [models.Index(fields=["status"])]
        constraints = [
            models.CheckConstraint(
                check=models.Q(amount__gte=0), name="payment_amount_nonnegative"
            )
        ]

    def __str__(self):
        return f"Payment {self.id} {self.amount} for {self.invoice.invoice_number}"


class PaymentEvidence(models.Model):
    payment = models.ForeignKey(
        Payment, on_delete=models.CASCADE, related_name="evidence"
    )
    file = models.FileField(upload_to="payment_evidence/")
    source = models.CharField(max_length=60, default="student_portal")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    checksum = models.CharField(max_length=64, blank=True, default="")

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"Evidence for {self.payment}"

    def public_label(self):
        return self.file.name.rsplit("/", 1)[-1]
