from django.urls import path

from dorm_system.rooms import views

app_name = "rooms"

urlpatterns = [
    path("", views.building_list, name="building_list"),
    path("rooms/", views.room_list, name="room_list"),
]
