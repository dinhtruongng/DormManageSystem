from dorm_system.billing.services import calculate_invoice_balance
from dorm_system.common.api import api_ok


def invoice_batch(request):
    """Generate recurring rent invoices for active residents (stub-friendly)."""
    from dorm_system.billing.models import Invoice
    from dorm_system.billing.services import generate_invoice
    from dorm_system.common.models import InvoiceItemType, StudentStatus
    from dorm_system.residents.models import Student

    created = 0
    for s in Student.objects.filter(status=StudentStatus.ACTIVE):
        generate_invoice(
            s,
            [
                {
                    "item_type": InvoiceItemType.RENT,
                    "description": "Monthly dormitory rent",
                    "unit_price": 1500000,
                    "amount": 1500000,
                }
            ],
        )
        created += 1
    return api_ok(f"Generated {created} recurring invoice(s).", {"created": created})


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
