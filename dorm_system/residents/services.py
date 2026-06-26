"""ResidentService: student CRUD, CSV import, and history (FR-02, §9.2)."""

import csv
import io
from dataclasses import dataclass, field

from django.db import transaction

from dorm_system.common.models import Gender, StudentStatus
from dorm_system.residents.models import Student


# CSV columns accepted by import_students (header row, case-insensitive).
IMPORT_COLUMNS = {"student_code", "full_name", "gender", "email", "phone"}


@dataclass
class StudentImportResult:
    """Outcome of a CSV import, surfaced to the admin upload view (§9.2)."""

    created: int = 0
    skipped: int = 0
    errors: list = field(default_factory=list)

    @property
    def total(self):
        return self.created + self.skipped + len(self.errors)


def create_student(data):
    """Validate uniqueness and create a student record."""
    if Student.objects.filter(student_code=data["student_code"]).exists():
        raise ValueError("student_code already exists")
    return Student.objects.create(**data)


@transaction.atomic
def import_students(csv_file):
    """Validate and import student rows from a CSV upload (FR-02, §9.2).

    Accepts a file-like opened in text mode or a Django UploadedFile (decoded
    here). Expected header columns: student_code, full_name, gender, email,
    phone (order-independent; gender optional). Returns a StudentImportResult.
    """
    result = StudentImportResult()

    # Accept both text files and binary Django uploads.
    raw = csv_file.read()
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(raw))
    if reader.fieldnames is None:
        result.errors.append("The file appears to be empty.")
        return result

    header = {h.strip().lower() for h in reader.fieldnames}
    missing = IMPORT_COLUMNS - header
    if missing:
        result.errors.append(
            f"Missing required column(s): {', '.join(sorted(missing))}."
        )
        return result

    valid_genders = {g.value for g in Gender}
    for lineno, row in enumerate(reader, start=2):  # line 1 is the header
        code = (row.get("student_code") or "").strip()
        name = (row.get("full_name") or "").strip()
        if not code or not name:
            result.skipped += 1
            result.errors.append(f"Line {lineno}: missing code or name, skipped.")
            continue
        if Student.objects.filter(student_code=code).exists():
            result.skipped += 1
            result.errors.append(f"Line {lineno}: student_code {code} already exists.")
            continue

        gender = (row.get("gender") or Gender.OTHER.value).strip().lower()
        if gender not in valid_genders:
            result.skipped += 1
            result.errors.append(
                f"Line {lineno}: invalid gender '{gender}', skipped."
            )
            continue

        Student.objects.create(
            student_code=code,
            full_name=name,
            gender=gender,
            email=(row.get("email") or "").strip(),
            phone=(row.get("phone") or "").strip(),
            status=StudentStatus.APPLICANT,
        )
        result.created += 1

    return result


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
