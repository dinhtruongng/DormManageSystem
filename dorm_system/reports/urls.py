from django.urls import path

from dorm_system.reports import views

app_name = "reports"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("occupancy/", views.occupancy, name="occupancy"),
    path("finance/", views.finance, name="finance"),
    path("audit/", views.audit, name="audit"),
]
