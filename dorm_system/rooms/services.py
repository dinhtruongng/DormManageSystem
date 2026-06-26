"""RoomInventoryService (report Section 9.4).

Owns the inventory mutations the report names: create_room, sync_beds, and
set_bed_status. Kept here (not in views) so the bed lifecycle transitions
match the state diagram and stay testable on their own.
"""

from django.db import transaction

from dorm_system.common.models import (
    AuditLog,
    BedStatus,
    RoomStatus,
    record_audit,
)
from dorm_system.rooms.models import Bed, Room


class BedStatusError(Exception):
    """Raised when a requested bed status transition is not legal."""


# Legal bed transitions derived from the report state diagram (§4.4).
_BED_TRANSITIONS = {
    BedStatus.AVAILABLE: {BedStatus.RESERVED, BedStatus.INACTIVE, BedStatus.CLEANING},
    BedStatus.RESERVED: {BedStatus.AVAILABLE, BedStatus.OCCUPIED},
    BedStatus.OCCUPIED: {BedStatus.CLEANING, BedStatus.AVAILABLE},
    BedStatus.CLEANING: {BedStatus.AVAILABLE, BedStatus.INACTIVE},
    BedStatus.INACTIVE: {BedStatus.CLEANING, BedStatus.AVAILABLE},
}


def _legal_transition(current, target):
    return target in _BED_TRANSITIONS.get(current, set())


@transaction.atomic
def create_room(floor, room_number, capacity, gender_policy, *, status=RoomStatus.OPEN):
    """Create a room and provision its beds in one operation (FR-03, §9.4)."""
    room = Room.objects.create(
        floor=floor,
        room_number=room_number,
        capacity=capacity,
        gender_policy=gender_policy,
        status=status,
    )
    sync_beds(room, capacity)
    return room


@transaction.atomic
def sync_beds(room, capacity):
    """Reconcile a room's bed count to its capacity (§9.4).

    Counts actual beds (not the capacity field, which is 0 only until beds
    exist). Adds missing beds when capacity rises; on a capacity reduction the
    existing beds are left in place rather than silently dropped, so a resident
    is never orphaned. The capacity field is always updated to the requested
    value so reporting reflects the intended configuration.
    """
    existing = room.beds.count()
    target = int(capacity)
    if target > existing:
        # Provision new beds for the additional slots.
        for slot in range(existing + 1, target + 1):
            Bed.objects.create(
                room=room,
                bed_code=f"{room.room_number}-B{slot}",
                position=f"Bed {slot}",
                status=BedStatus.AVAILABLE,
            )
    room.capacity = target
    room.save(update_fields=["capacity"])
    return room


@transaction.atomic
def set_bed_status(bed, status, *, reason="", actor=None):
    """Validate a bed lifecycle transition, apply it, and audit it (§9.4).

    Mirrors the §4.4 bed state diagram: illegal jumps raise BedStatusError
    instead of silently corrupting inventory.
    """
    bed = Bed.objects.select_for_update().get(pk=bed.pk)
    status = BedStatus(status) if not isinstance(status, BedStatus) else status
    if bed.status != status and not _legal_transition(bed.status, status):
        raise BedStatusError(
            f"Illegal bed transition: {bed.status} -> {status}."
        )
    old_status = bed.status
    bed.status = status
    bed.save(update_fields=["status"])
    record_audit(
        actor,
        "set_bed_status",
        "bed",
        bed.id,
        old_value={"status": old_status},
        new_value={"status": bed.status},
        reason=reason,
    )
    return bed


__all__ = ["BedStatusError", "create_room", "sync_beds", "set_bed_status"]
