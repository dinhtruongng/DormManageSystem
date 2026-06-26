from django.urls import path

from dorm_system.assignments import views

app_name = "assignments"

urlpatterns = [
    path("recommend/<int:student_id>/", views.recommend, name="recommend"),
    path("reserve/<int:student_id>/<int:bed_id>/", views.reserve, name="reserve"),
    path("<int:assignment_id>/", views.detail, name="detail"),
    path("<int:assignment_id>/check-in/", views.check_in, name="check_in"),
    path("<int:assignment_id>/checkout/", views.checkout_form, name="checkout_form"),
    path("<int:assignment_id>/settle/", views.settle, name="settle"),
]
