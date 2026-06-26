from django.urls import path

from dorm_system.communications import views

app_name = "communications"

urlpatterns = [
    path("announcements/", views.announcement_list, name="list"),
    path("announcements/new/", views.announcement_create, name="create"),
]
