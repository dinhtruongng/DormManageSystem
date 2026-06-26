from dorm_system.common.api import api_ok
from dorm_system.common.models import BedStatus
from dorm_system.rooms.models import Bed, Room


def room_list(request):
    status = request.GET.get("status")
    qs = Room.objects.select_related("floor__building").all()
    rows = [
        {
            "roomId": r.id,
            "building": r.floor.building.name,
            "floor": r.floor.floor_number,
            "roomNumber": r.room_number,
            "capacity": r.capacity,
            "status": r.status,
        }
        for r in qs
    ]
    return api_ok("Room list.", {"rooms": rows})


def bed_list(request):
    qs = Bed.objects.select_related("room__floor__building").all()
    status = request.GET.get("status")
    if status:
        qs = qs.filter(status=status)
    rows = [
        {
            "bedId": b.id,
            "bedCode": b.bed_code,
            "room": b.room.room_number,
            "building": b.room.floor.building.name,
            "status": b.status,
        }
        for b in qs
    ]
    return api_ok("Bed list.", {"beds": rows, "status": status})
