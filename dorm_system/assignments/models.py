from django.conf import settings
from django.db import models

from dorm_system.common.models import (
    AssignmentStatus,
    BedStatus,
    InspectionType,
    StudentStatus,
)
from dorm_system.residents.models import Student
from dorm_system.rooms.models import Bed


class AssignmentManager(models.Manager):
    def active(self):
        return self.filter(status__in=(AssignmentStatus.RESERVED, AssignmentStatus.ACTIVE))


class Assignment(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.PROTECT, related_name="assignments"
    )
    bed = models.ForeignKey(Bed, on_delete=models.PROTECT, related_name="assignments")
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="assignments_made",
    )
    status = models.CharField(
        max_length=16, choices=AssignmentStatus.choices, default=AssignmentStatus.RESERVED
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    reason = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    objects = AssignmentManager()

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            # At most one active/reserved assignment per student.
            models.UniqueConstraint(
                fields=["student"],
                condition=models.Q(
                    status__in=(AssignmentStatus.RESERVED, AssignmentStatus.ACTIVE)
                ),
                name="one_active_assignment_per_student",
            ),
            # At most one active/reserved assignment per bed (prevents double booking).
            models.UniqueConstraint(
                fields=["bed"],
                condition=models.Q(
                    status__in=(AssignmentStatus.RESERVED, AssignmentStatus.ACTIVE)
                ),
                name="one_active_assignment_per_bed",
            ),
        ]
        indexes = [models.Index(fields=["status"])]

    def __str__(self):
        return f"{self.student} -> {self.bed} ({self.get_status_display()})"


class Inspection(models.Model):
    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name="inspections"
    )
    inspected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="inspections_made",
    )
    type = models.CharField(max_length=16, choices=InspectionType.choices)
    condition_summary = models.TextField(blank=True, default="")
    damage_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    needs_cleaning = models.BooleanField(default=False)
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_type_display()} for {self.assignment}"
