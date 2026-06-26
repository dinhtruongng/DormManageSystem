"""Room inventory views: buildings, rooms, beds with availability."""

from django.shortcuts import render

from dorm_system.accounts.permissions import role_required
from dorm_system.common.models import BedStatus, Role
from dorm_system.rooms.models import Bed, Building, Room


@role_required(Role.ADMIN, Role.SYSADMIN)
def building_list(request):
    buildings = []
    for b in Building.objects.all():
        beds = Bed.objects.filter(room__floor__building=b)
        buildings.append(
            {
                "obj": b,
                "total": beds.count(),
                "occupied": beds.filter(status=BedStatus.OCCUPIED).count(),
                "available": beds.filter(status=BedStatus.AVAILABLE).count(),
            }
        )
    return render(request, "rooms/building_list.html", {"buildings": buildings})


@role_required(Role.ADMIN, Role.SYSADMIN)
def room_list(request):
    rooms = Room.objects.select_related("floor__building").all()
    rows = []
    for r in rooms:
        beds = list(r.beds.all())
        rows.append(
            {
                "room": r,
                "building": r.floor.building.name,
                "floor": r.floor.floor_number,
                "available": sum(1 for b in beds if b.status == BedStatus.AVAILABLE),
                "total": len(beds),
                "beds": beds,
            }
        )
    return render(request, "rooms/room_list.html", {"rooms": rows})
