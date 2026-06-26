from django.core.files.uploadedfile import UploadedFile

from dorm_system.common.api import api_fail, api_ok
from dorm_system.payments.models import Payment
from dorm_system.payments.services import (
    PermissionDenied,
    confirm_payment,
    reject_payment,
    submit_payment_evidence,
)


def payment_create(request):
    invoice_id = request.POST.get("invoiceId")
    try:
        amount = float(request.POST.get("amount", 0))
    except ValueError:
        amount = 0
    files = request.FILES.getlist("evidenceFiles") or request.FILES.getlist("evidence")
    student = getattr(request.user, "student", None)
    if student is None or invoice_id is None:
        return api_fail("Missing student or invoice.", status=400)
    from dorm_system.billing.models import Invoice

    try:
        invoice = Invoice.objects.get(pk=invoice_id)
    except Invoice.DoesNotExist:
        return api_fail("Invoice not found.", status=404)
    try:
        payment = submit_payment_evidence(invoice, amount, files, student)
    except (PermissionDenied, ValueError) as exc:
        return api_fail(str(exc), status=422)
    return api_ok(
        "Payment evidence submitted for finance review.",
        {
            "paymentId": payment.id,
            "invoiceId": invoice.id,
            "status": payment.status,
            "evidenceCount": payment.evidence.count(),
        },
        # 201
    )


def _payment_create_response(*args, **kwargs):
    resp = payment_create(*args, **kwargs)
    resp.status_code = 201
    return resp


def payment_confirm(request, payment_id):
    try:
        payment = Payment.objects.get(pk=payment_id)
        confirm_payment(payment, request.user)
    except Payment.DoesNotExist:
        return api_fail("Payment not found.", status=404)
    except PermissionDenied as exc:
        return api_fail(str(exc), status=409)
    return api_ok("Payment confirmed.", {"paymentId": payment.id})


def payment_reject(request, payment_id):
    try:
        payment = Payment.objects.get(pk=payment_id)
        reject_payment(payment, request.user)
    except Payment.DoesNotExist:
        return api_fail("Payment not found.", status=404)
    except PermissionDenied as exc:
        return api_fail(str(exc), status=409)
    return api_ok("Payment rejected.", {"paymentId": payment.id})
