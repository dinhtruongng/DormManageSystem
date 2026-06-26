"""Payment review views: upload form, review queue, confirm/reject."""

from django.contrib import messages as django_messages
from django.shortcuts import get_object_or_404, redirect, render

from dorm_system.accounts.permissions import role_required
from dorm_system.billing.services import calculate_invoice_balance
from dorm_system.common.models import Role
from dorm_system.payments.forms import PaymentUploadForm
from dorm_system.payments.models import Payment
from dorm_system.payments.services import (
    PermissionDenied,
    confirm_payment,
    reject_payment,
    submit_payment_evidence,
)


@role_required(Role.STUDENT)
def upload(request, invoice_id):
    from dorm_system.billing.models import Invoice

    invoice = get_object_or_404(Invoice, pk=invoice_id)
    student = request.user.student
    if invoice.student_id != student.id:
        django_messages.error(request, "You can only pay your own invoices.")
        return redirect("residents:me")

    if request.method == "POST":
        form = PaymentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist("evidence")
            try:
                submit_payment_evidence(
                    invoice, form.cleaned_data["amount"], files, student
                )
                django_messages.success(
                    request,
                    "Payment evidence submitted. Finance will review it shortly.",
                )
                return redirect("residents:me")
            except (PermissionDenied, ValueError) as exc:
                form.add_error(None, str(exc))
    else:
        form = PaymentUploadForm(initial={"amount": invoice.balance_due()})
    return render(
        request,
        "payments/upload.html",
        {"form": form, "invoice": invoice},
    )


@role_required(Role.FINANCE, Role.ADMIN)
def review(request):
    payments = Payment.objects.select_related("invoice", "student", "reviewed_by").filter(
        status="pending_review"
    )
    rows = [
        {
            "payment": p,
            "evidence": list(p.evidence.all()),
            "balance": calculate_invoice_balance(p.invoice),
        }
        for p in payments
    ]
    return render(request, "payments/review.html", {"rows": rows})


@role_required(Role.FINANCE, Role.ADMIN)
def confirm(request, payment_id):
    payment = get_object_or_404(Payment, pk=payment_id)
    try:
        confirm_payment(payment, request.user, note=request.POST.get("note", ""))
        django_messages.success(request, "Payment confirmed. Invoice updated.")
    except PermissionDenied as exc:
        django_messages.error(request, str(exc))
    return redirect("payments:review")


@role_required(Role.FINANCE, Role.ADMIN)
def reject(request, payment_id):
    payment = get_object_or_404(Payment, pk=payment_id)
    try:
        reject_payment(payment, request.user, note=request.POST.get("note", ""))
        django_messages.success(request, "Payment rejected. Outstanding balance unchanged.")
    except PermissionDenied as exc:
        django_messages.error(request, str(exc))
    return redirect("payments:review")


@role_required(Role.FINANCE, Role.ADMIN)
def history(request):
    payments = Payment.objects.select_related("invoice", "student", "reviewed_by").exclude(
        status="pending_review"
    )
    return render(request, "payments/history.html", {"payments": payments})
