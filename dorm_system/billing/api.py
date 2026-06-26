from dorm_system.billing.services import calculate_invoice_balance, generate_recurring_rent
from dorm_system.common.api import api_ok


def invoice_batch(request):
    """Generate recurring rent invoices for active residents (§9.7, FR-08)."""
    invoices = generate_recurring_rent()
    return api_ok(
        f"Generated {len(invoices)} recurring invoice(s).", {"created": len(invoices)}
    )


def student_invoices(request):
    """Invoice list for the calling student (/students/me/invoices)."""
    student = getattr(request.user, "student", None)
    if student is None:
        return api_ok("No student record.", {"invoices": []})
    rows = [
        {
            "invoiceId": i.id,
            "invoiceNumber": i.invoice_number,
            "dueDate": i.due_date.isoformat(),
            "status": i.status,
            "outstanding": float(calculate_invoice_balance(i)["outstanding"]),
        }
        for i in student.invoices.all()
    ]
    return api_ok("Student invoices.", {"invoices": rows})
