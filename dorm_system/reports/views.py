"""Reporting views: dashboard, occupancy, finance, audit trail (FR-12, FR-13).

Also exposes CSV exports for the occupancy and finance reports (§8.10, §9.10),
matching the report's "downloadable summaries" requirement.
"""

import csv

from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from dorm_system.accounts.permissions import role_required
from dorm_system.common.models import AuditLog, Role
from dorm_system.reports.services import (
    dashboard_summary,
    finance_report,
    finance_report_rows,
    occupancy_report,
)


def _csv_response(filename, header, rows):
    """Stream a CSV download with a BOM-safe UTF-8 header (§9.10)."""
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow(header)
    for row in rows:
        writer.writerow(row)
    return response


@role_required(Role.ADMIN, Role.FINANCE, Role.SYSADMIN)
def dashboard(request):
    summary = dashboard_summary()
    occupancy = occupancy_report()
    audit = AuditLog.objects.select_related("actor")[:15]
    return render(
        request,
        "reports/dashboard.html",
        {"summary": summary, "occupancy": occupancy, "audit": audit},
    )


@role_required(Role.ADMIN, Role.FINANCE, Role.SYSADMIN)
def occupancy(request):
    return render(request, "reports/occupancy.html", {"rows": occupancy_report()})


@role_required(Role.FINANCE, Role.ADMIN)
def finance(request):
    return render(request, "reports/finance.html", {"report": finance_report()})


@role_required(Role.ADMIN, Role.FINANCE, Role.SYSADMIN)
def audit(request):
    return render(
        request,
        "reports/audit.html",
        {"entries": AuditLog.objects.select_related("actor")[:200]},
    )


@role_required(Role.ADMIN, Role.FINANCE, Role.SYSADMIN)
def occupancy_export(request):
    """Occupancy report as CSV download (§8.10, §9.10)."""
    stamp = timezone.now().strftime("%Y%m%d")
    header = ["building", "total_beds", "occupied", "available", "occupancy_rate_%"]
    rows = [
        [r["building"], r["total_beds"], r["occupied"], r["available"], r["rate"]]
        for r in occupancy_report()
    ]
    return _csv_response(f"occupancy-{stamp}.csv", header, rows)


@role_required(Role.FINANCE, Role.ADMIN)
def finance_export(request):
    """Finance receivables report as CSV download (§8.10, §9.10)."""
    stamp = timezone.now().strftime("%Y%m%d")
    header = [
        "invoice_number",
        "student",
        "student_code",
        "status",
        "total",
        "outstanding",
        "due_date",
    ]
    rows = [
        [
            r["invoice_number"],
            r["student"],
            r["student_code"],
            r["status"],
            r["total"],
            r["outstanding"],
            r["due_date"],
        ]
        for r in finance_report_rows()
    ]
    return _csv_response(f"finance-{stamp}.csv", header, rows)
