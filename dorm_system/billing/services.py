"""BillingService: invoice generation, balances, overdue marking.

Implements report Section 8.1 / pseudocode. Pending payments do NOT reduce the
outstanding balance until confirmed (NFR-02, FR-10).
"""

from datetime import date, timedelta

from django.db import transaction

from dorm_system.billing.models import Invoice, InvoiceLine
from dorm_system.common.models import (
    InvoiceItemType,
    InvoiceStatus,
    PaymentStatus,
)


def calculate_invoice_balance(invoice):
    """InvoiceBalance structure (report Section 7.7)."""
    total = invoice.total_amount()
    confirmed = sum(
        p.amount for p in invoice.payments.filter(status=PaymentStatus.CONFIRMED)
    ) or 0
    pending = sum(
        p.amount for p in invoice.payments.filter(status=PaymentStatus.PENDING_REVIEW)
    ) or 0
    rejected = sum(
        p.amount for p in invoice.payments.filter(status=PaymentStatus.REJECTED)
    ) or 0
    outstanding = max(total - confirmed, 0)
    return {
        "total": total,
        "confirmed": confirmed,
        "pending": pending,
        "rejected": rejected,
        "outstanding": outstanding,
    }


def calculate_student_balance(student):
    """Sum of outstanding balances across a student's open invoices."""
    total = 0
    for invoice in student.invoices.exclude(status=InvoiceStatus.CANCELLED):
        total += calculate_invoice_balance(invoice)["outstanding"]
    return total


def _derive_status(balance):
    """Map a balance back to the invoice status enum."""
    outstanding = balance["outstanding"]
    if outstanding <= 0:
        return InvoiceStatus.PAID
    if balance["confirmed"] > 0:
        return InvoiceStatus.PARTIALLY_PAID
    return InvoiceStatus.ISSUED


def refresh_invoice_status(invoice):
    """Recompute and persist invoice status after a payment decision."""
    balance = calculate_invoice_balance(invoice)
    invoice.status = _derive_status(balance)
    invoice.save(update_fields=["status"])
    return invoice


@transaction.atomic
def generate_invoice(student, lines, due_in_days=30, *, deposit=None, rent=None):
    """Create an invoice with one or more charge lines (FR-08)."""
    today = date.today()
    seq = Invoice.objects.count() + 1
    invoice = Invoice.objects.create(
        student=student,
        invoice_number=f"INV-{today.year}-{seq:04d}",
        due_date=today + timedelta(days=due_in_days),
        status=InvoiceStatus.ISSUED,
    )
    for item in lines:
        InvoiceLine.objects.create(
            invoice=invoice,
            item_type=item.get("item_type", InvoiceItemType.FEE),
            description=item.get("description", ""),
            quantity=item.get("quantity", 1),
            unit_price=item.get("unit_price", 0),
            amount=item.get("amount", item.get("unit_price", 0)),
        )
    return invoice


def generate_initial_invoice(student, assignment, *, rent=1500000, deposit=1500000):
    """Deposit + first rent for a freshly reserved bed (FR-06/FR-08)."""
    return generate_invoice(
        student,
        [
            {
                "item_type": InvoiceItemType.RENT,
                "description": "Dormitory rent - first cycle",
                "unit_price": rent,
                "amount": rent,
            },
            {
                "item_type": InvoiceItemType.DEPOSIT,
                "description": "Refundable deposit",
                "unit_price": deposit,
                "amount": deposit,
            },
        ],
    )


def mark_overdue_invoices(today=None):
    """Move issued/partially-paid invoices past due to overdue status."""
    today = today or date.today()
    updated = []
    for invoice in Invoice.objects.filter(
        status__in=(InvoiceStatus.ISSUED, InvoiceStatus.PARTIALLY_PAID),
        due_date__lt=today,
    ):
        invoice.status = InvoiceStatus.OVERDUE
        invoice.save(update_fields=["status"])
        updated.append(invoice)
    return updated
