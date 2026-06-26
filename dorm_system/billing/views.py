"""Billing views: invoice list, invoice detail with balance breakdown."""

from django.shortcuts import get_object_or_404, render

from dorm_system.accounts.permissions import role_required
from dorm_system.billing.services import calculate_invoice_balance, mark_overdue_invoices
from dorm_system.common.models import InvoiceStatus, Role
from dorm_system.residents.models import Student


@role_required(Role.ADMIN, Role.FINANCE)
def invoice_list(request):
    status = request.GET.get("status", "").strip()
    mark_overdue_invoices()  # keep displayed statuses fresh
    invoices = _all_invoices()
    if status:
        invoices = [i for i in invoices if i.status == status]
    rows = [
        {"invoice": i, "balance": calculate_invoice_balance(i)} for i in invoices
    ]
    return render(
        request,
        "billing/invoice_list.html",
        {"rows": rows, "status": status, "statuses": InvoiceStatus.choices},
    )


@role_required(Role.ADMIN, Role.FINANCE)
def invoice_detail(request, pk):
    from dorm_system.billing.models import Invoice

    invoice = get_object_or_404(Invoice, pk=pk)
    return render(
        request,
        "billing/invoice_detail.html",
        {
            "invoice": invoice,
            "balance": calculate_invoice_balance(invoice),
            "lines": invoice.lines.all(),
            "payments": invoice.payments.all(),
        },
    )


def _all_invoices():
    from dorm_system.billing.models import Invoice

    return list(Invoice.objects.select_related("student").all())
