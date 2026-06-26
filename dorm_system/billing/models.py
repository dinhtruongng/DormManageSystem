from django.db import models

from dorm_system.common.models import InvoiceItemType, InvoiceStatus
from dorm_system.residents.models import Student


class InvoiceManager(models.Manager):
    def overdue(self):
        from datetime import date

        return self.filter(
            status__in=(InvoiceStatus.ISSUED, InvoiceStatus.PARTIALLY_PAID),
            due_date__lt=date.today(),
        )


class Invoice(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.PROTECT, related_name="invoices"
    )
    invoice_number = models.CharField(max_length=32, unique=True)
    due_date = models.DateField()
    status = models.CharField(
        max_length=20, choices=InvoiceStatus.choices, default=InvoiceStatus.ISSUED
    )
    created_at = models.DateTimeField(auto_now_add=True)

    objects = InvoiceManager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["due_date"]),
        ]

    def __str__(self):
        return self.invoice_number

    def total_amount(self):
        return sum(line.amount for line in self.lines.all()) or 0

    def balance_due(self):
        from dorm_system.billing.services import calculate_invoice_balance

        return calculate_invoice_balance(self)["outstanding"]


class InvoiceLine(models.Model):
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="lines"
    )
    item_type = models.CharField(max_length=16, choices=InvoiceItemType.choices)
    description = models.CharField(max_length=200, blank=True, default="")
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.get_item_type_display()}"
