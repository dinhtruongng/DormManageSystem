"""Versioned API routes under /api/v1.

Maps the REST-style contract from the report (Section 8.7). HTML routes remain
the primary demo surface; these JSON endpoints support dashboard widgets,
recommendations, and future clients.
"""

from django.urls import path

from dorm_system.reports import api as reports_api
from dorm_system.residents import api as residents_api
from dorm_system.rooms import api as rooms_api
from dorm_system.assignments import api as assignments_api
from dorm_system.billing import api as billing_api
from dorm_system.payments import api as payments_api
from dorm_system.communications import api as communications_api

urlpatterns = [
    path("dashboard-summary", reports_api.dashboard_summary, name="dashboard-summary"),
    path("students", residents_api.student_list, name="students"),
    path("students/me/invoices", billing_api.student_invoices, name="student-invoices"),
    path("rooms", rooms_api.room_list, name="rooms"),
    path("beds", rooms_api.bed_list, name="beds"),
    path("assignment-recommendations", assignments_api.recommendations, name="assignment-recommendations"),
    path("assignments", assignments_api.assignment_create, name="assignment-create"),
    path(
        "assignments/<int:assignment_id>/check-in",
        assignments_api.check_in,
        name="assignment-check-in",
    ),
    path(
        "assignments/<int:assignment_id>/check-out",
        assignments_api.check_out,
        name="assignment-check-out",
    ),
    path("invoices/batches", billing_api.invoice_batch, name="invoice-batch"),
    path("payments", payments_api.payment_create, name="payment-create"),
    path("payments/<int:payment_id>/confirm", payments_api.payment_confirm, name="payment-confirm"),
    path("payments/<int:payment_id>/reject", payments_api.payment_reject, name="payment-reject"),
    path("announcements", communications_api.announcement_create, name="announcement-create"),
    path("reports/occupancy", reports_api.occupancy_report, name="occupancy-report"),
]
