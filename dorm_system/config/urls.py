"""Root URL configuration wiring all feature apps together.

Layered per the report: HTML routes serve the server-rendered demo, while
`/api/v1` exposes the documented REST-style JSON contracts.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from dorm_system.accounts import views as accounts_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", accounts_views.home, name="home"),
    path("auth/", include(("dorm_system.accounts.urls", "accounts"), namespace="accounts")),
    path("residents/", include(("dorm_system.residents.urls", "residents"), namespace="residents")),
    path("rooms/", include(("dorm_system.rooms.urls", "rooms"), namespace="rooms")),
    path("assignments/", include(("dorm_system.assignments.urls", "assignments"), namespace="assignments")),
    path("billing/", include(("dorm_system.billing.urls", "billing"), namespace="billing")),
    path("payments/", include(("dorm_system.payments.urls", "payments"), namespace="payments")),
    path("communications/", include(("dorm_system.communications.urls", "communications"), namespace="communications")),
    path("reports/", include(("dorm_system.reports.urls", "reports"), namespace="reports")),
    path("api/v1/", include(("dorm_system.config.api_urls", "api"), namespace="api")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
