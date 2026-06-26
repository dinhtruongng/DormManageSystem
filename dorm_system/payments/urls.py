from django.urls import path

from dorm_system.payments import views

app_name = "payments"

urlpatterns = [
    path("upload/<int:invoice_id>/", views.upload, name="upload"),
    path("review/", views.review, name="review"),
    path("<int:payment_id>/confirm/", views.confirm, name="confirm"),
    path("<int:payment_id>/reject/", views.reject, name="reject"),
    path("history/", views.history, name="history"),
]
