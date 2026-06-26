from dorm_system.common.api import api_ok
from dorm_system.reports.services import (
    dashboard_summary as _dashboard_summary,
    occupancy_report as _occupancy_report,
)


def dashboard_summary(request):
    return api_ok("Dashboard summary.", _dashboard_summary())


def occupancy_report(request):
    return api_ok("Occupancy report.", {"rows": _occupancy_report()})
