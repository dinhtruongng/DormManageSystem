from django.urls import path

from dorm_system.residents import views

app_name = "residents"

urlpatterns = [
    path("", views.student_list, name="student_list"),
    path("import/", views.student_import, name="student_import"),
    path("<int:pk>/", views.student_detail, name="student_detail"),
    path("me/", views.me, name="me"),
]
