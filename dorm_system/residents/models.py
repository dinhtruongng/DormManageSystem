from django.conf import settings
from django.db import models

from dorm_system.common.models import Gender, StudentStatus


class Student(models.Model):
    """Student master record (FR-02). Linked 0..1 to a Django auth user."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="student",
        null=True,
        blank=True,
    )
    student_code = models.CharField(max_length=32, unique=True)
    full_name = models.CharField(max_length=150)
    gender = models.CharField(max_length=12, choices=Gender.choices, default=Gender.OTHER)
    email = models.EmailField(blank=True, default="")
    phone = models.CharField(max_length=20, blank=True, default="")
    status = models.CharField(
        max_length=20, choices=StudentStatus.choices, default=StudentStatus.APPLICANT
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["full_name"]
        indexes = [models.Index(fields=["status"])]

    def __str__(self):
        return f"{self.full_name} ({self.student_code})"

    def active_assignment(self):
        return self.assignments.filter(
            status__in=("reserved", "active")
        ).select_related("bed__room__floor__building").first()

    def balance_due(self):
        from dorm_system.billing.services import calculate_student_balance

        return calculate_student_balance(self)
