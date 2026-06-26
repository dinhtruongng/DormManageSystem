from django.urls import path

from dorm_system.reports import views

app_name = "reports"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("occupancy/", views.occupancy, name="occupancy"),
    path("occupancy/export/", views.occupancy_export, name="occupancy_export"),
    path("finance/", views.finance, name="finance"),
    path("finance/export/", views.finance_export, name="finance_export"),
    path("audit/", views.audit, name="audit"),
]
