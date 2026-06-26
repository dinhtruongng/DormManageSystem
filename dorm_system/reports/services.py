"""ReportingService: dashboard metrics and aggregate queries (FR-12)."""

from collections import Counter

from dorm_system.assignments.models import Assignment, AssignmentStatus
from dorm_system.billing.models import Invoice
from dorm_system.billing.services import calculate_invoice_balance
from dorm_system.common.models import BedStatus, InvoiceStatus, PaymentStatus, StudentStatus
from dorm_system.payments.models import Payment
from dorm_system.residents.models import Student
from dorm_system.rooms.models import Bed, Building


def dashboard_summary():
    """DashboardSummary structure (report Section 7.7)."""
    from datetime import date

    bed_counts = Counter(b["status"] for b in Bed.objects.values("status"))
    return {
        "total_students": Student.objects.count(),
        "active_students": Student.objects.filter(status=StudentStatus.ACTIVE).count(),
        "occupied_beds": bed_counts.get(BedStatus.OCCUPIED, 0),
        "available_beds": bed_counts.get(BedStatus.AVAILABLE, 0),
        "reserved_beds": bed_counts.get(BedStatus.RESERVED, 0),
        "cleaning_beds": bed_counts.get(BedStatus.CLEANING, 0),
        "pending_payments": Payment.objects.filter(status=PaymentStatus.PENDING_REVIEW).count(),
        "overdue_invoices": Invoice.objects.filter(status=InvoiceStatus.OVERDUE).count(),
        "active_assignments": Assignment.objects.filter(
            status__in=(AssignmentStatus.RESERVED, AssignmentStatus.ACTIVE)
        ).count(),
    }


def occupancy_report():
    """Per-building occupancy breakdown (FR-12)."""
    rows = []
    for building in Building.objects.all():
        beds = Bed.objects.filter(room__floor__building=building)
        total = beds.count()
        occupied = beds.filter(status=BedStatus.OCCUPIED).count()
        available = beds.filter(status=BedStatus.AVAILABLE).count()
        rate = (occupied / total * 100) if total else 0
        rows.append(
            {
                "building": building.name,
                "total_beds": total,
                "occupied": occupied,
                "available": available,
                "rate": round(rate, 1),
            }
        )
    return rows


def finance_report():
    """Outstanding balances and payment-review queue (FR-12)."""
    outstanding = 0
    for invoice in Invoice.objects.exclude(status=InvoiceStatus.CANCELLED):
        outstanding += calculate_invoice_balance(invoice)["outstanding"]
    return {
        "outstanding_total": outstanding,
        "pending_payments": Payment.objects.filter(status=PaymentStatus.PENDING_REVIEW).count(),
        "overdue": Invoice.objects.filter(status=InvoiceStatus.OVERDUE).count(),
    }
