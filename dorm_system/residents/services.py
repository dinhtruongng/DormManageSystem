"""ResidentService: student CRUD and history (FR-02)."""

from dorm_system.common.models import StudentStatus
from dorm_system.residents.models import Student


def create_student(data):
    """Validate uniqueness and create a student record."""
    if Student.objects.filter(student_code=data["student_code"]).exists():
        raise ValueError("student_code already exists")
    return Student.objects.create(**data)


def get_resident_history(student):
    """Return assignments, invoices, and inspections for a student."""
    return {
        "assignments": list(student.assignments.all()),
        "invoices": list(student.invoices.all()),
        "inspections": [
            ins
            for a in student.assignments.all()
            for ins in a.inspections.all()
        ],
    }


def deactivate_student(student):
    student.status = StudentStatus.INACTIVE
    student.save(update_fields=["status"])
    return student
