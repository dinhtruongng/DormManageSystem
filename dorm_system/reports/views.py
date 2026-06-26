"""Reporting views: dashboard, occupancy, finance, audit trail (FR-12, FR-13)."""

from django.shortcuts import render

from dorm_system.accounts.permissions import role_required
from dorm_system.common.models import AuditLog, Role
from dorm_system.reports.services import dashboard_summary, finance_report, occupancy_report


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
