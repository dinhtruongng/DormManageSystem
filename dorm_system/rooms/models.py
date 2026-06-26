from django.db import models

from dorm_system.common.models import (
    BedStatus,
    BuildingStatus,
    GenderPolicy,
    RoomStatus,
)


class Building(models.Model):
    name = models.CharField(max_length=80)
    address = models.CharField(max_length=200, blank=True, default="")
    status = models.CharField(
        max_length=16, choices=BuildingStatus.choices, default=BuildingStatus.ACTIVE
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Floor(models.Model):
    building = models.ForeignKey(
        Building, on_delete=models.CASCADE, related_name="floors"
    )
    floor_number = models.IntegerField()

    class Meta:
        ordering = ["building__name", "floor_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["building", "floor_number"], name="unique_floor_per_building"
            )
        ]

    def __str__(self):
        return f"{self.building.name} - Floor {self.floor_number}"


class Room(models.Model):
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name="rooms")
    room_number = models.CharField(max_length=20)
    capacity = models.PositiveIntegerField(default=2)
    gender_policy = models.CharField(
        max_length=16, choices=GenderPolicy.choices, default=GenderPolicy.MIXED
    )
    status = models.CharField(
        max_length=16, choices=RoomStatus.choices, default=RoomStatus.OPEN
    )

    class Meta:
        ordering = ["floor__building__name", "floor__floor_number", "room_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["floor", "room_number"], name="unique_room_per_floor"
            )
        ]

    def __str__(self):
        return f"{self.floor.building.name} {self.room_number}"

    def accepts(self, student):
        """Gender policy check used by the assignment scorer (FR-04)."""
        if self.gender_policy == GenderPolicy.UNSPECIFIED:
            return True
        if self.gender_policy == GenderPolicy.MIXED:
            return True
        return self.gender_policy == student.gender

    def available_bed_count(self):
        return self.beds.filter(status=BedStatus.AVAILABLE).count()


class BedManager(models.Manager):
    def available(self):
        return self.filter(status=BedStatus.AVAILABLE)


class Bed(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="beds")
    bed_code = models.CharField(max_length=24)
    position = models.CharField(max_length=24, blank=True, default="")
    status = models.CharField(
        max_length=16, choices=BedStatus.choices, default=BedStatus.AVAILABLE
    )

    objects = BedManager()

    class Meta:
        ordering = ["room__floor__building__name", "room__room_number", "bed_code"]
        constraints = [
            models.UniqueConstraint(
                fields=["room", "bed_code"], name="unique_bed_per_room"
            )
        ]
        indexes = [models.Index(fields=["status"])]

    def __str__(self):
        return f"{self.room} - {self.bed_code}"
