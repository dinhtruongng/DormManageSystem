"""Demo Data module (FR-14): build a realistic demo dataset.

Creates users for each role, buildings/floors/rooms/beds with mixed occupancy,
students across all statuses, assignments, invoices, and pending payments so
every dashboard and workflow in the report is exercisable.
"""

from datetime import date, timedelta

from django.contrib.auth import get_user_model

from dorm_system.accounts.models import UserProfile
from dorm_system.assignments.models import Assignment
from dorm_system.assignments.services import activate_assignment, reserve_bed
from dorm_system.billing.models import Invoice
from dorm_system.billing.services import generate_initial_invoice, mark_overdue_invoices
from dorm_system.common.models import (
    AssignmentStatus,
    Audience,
    BedStatus,
    Gender,
    GenderPolicy,
    InvoiceItemType,
    InvoiceStatus,
    PaymentMethod,
    PaymentStatus,
    Role,
    StudentStatus,
)
from dorm_system.communications.models import Announcement
from dorm_system.payments.models import Payment, PaymentEvidence
from dorm_system.residents.models import Student
from dorm_system.rooms.models import Bed, Building, Floor, Room

User = get_user_model()

FIRST_NAMES = ["Nguyen", "Tran", "Le", "Pham", "Hoang", "Phan", "Vu", "Dang", "Bui", "Do"]
LAST_NAMES = ["Van A", "Thi B", "Minh C", "Hoa D", "Quoc E", "Linh F", "Anh G", "Ngoc H", "Tuan I", "Mai J"]


def _user(username, role, password):
    user, _ = User.objects.get_or_create(
        username=username,
        defaults={"email": f"{username}@example.edu", "first_name": username.title()},
    )
    user.set_password(password)
    user.save()
    UserProfile.objects.update_or_create(user=user, defaults={"role": role})
    return user


def seed():
    if Student.objects.exists():
        print("Demo data already present; skipping seed. Run `flush` first to rebuild.")
        return

    # --- Roles / accounts ---
    admin = _user("admin", Role.ADMIN, "admin")
    finance = _user("finance", Role.FINANCE, "finance")
    sysadmin = _user("sysadmin", Role.SYSADMIN, "sysadmin")

    # --- Buildings / floors / rooms / beds ---
    buildings = []
    for bname, floors in [("Building A", 3), ("Building B", 2)]:
        b = Building.objects.create(name=bname, address=f"{bname} Campus Road")
        for fn in range(1, floors + 1):
            floor = Floor.objects.create(building=b, floor_number=fn)
            for rn in range(1, 5):
                policy = GenderPolicy.MIXED if (fn + rn) % 2 == 0 else GenderPolicy.MALE
                if bname == "Building B" and fn == 1:
                    policy = GenderPolicy.FEMALE
                room = Room.objects.create(
                    floor=floor,
                    room_number=f"{bname[-1]}{fn}0{rn}",
                    capacity=2,
                    gender_policy=policy,
                )
                for bn in range(1, 3):
                    Bed.objects.create(
                        room=room,
                        bed_code=f"{room.room_number}-B{bn}",
                        position=f"Bed {bn}",
                        status=BedStatus.AVAILABLE,
                    )
        buildings.append(b)

    # --- Students (with login accounts) ---
    students = []
    genders = [Gender.MALE, Gender.FEMALE, Gender.OTHER]
    for i in range(12):
        uname = f"student{i+1:02d}"
        user = _user(uname, Role.STUDENT, "student")
        s = Student.objects.create(
            user=user,
            student_code=f"SE{2026000 + i}",
            full_name=f"{FIRST_NAMES[i % len(FIRST_NAMES)]} {LAST_NAMES[i % len(LAST_NAMES)]}",
            gender=genders[i % len(genders)],
            email=user.email,
            phone=f"090100{i:04d}",
            status=StudentStatus.APPLICANT,
        )
        students.append(s)

    # Generic applicants/students without logins (for search density)
    for i in range(12, 24):
        Student.objects.create(
            student_code=f"SE{2026000 + i}",
            full_name=f"{FIRST_NAMES[i % len(FIRST_NAMES)]} {LAST_NAMES[i % len(LAST_NAMES)]}",
            gender=genders[i % len(genders)],
            email=f"se{2026000+i}@example.edu",
            phone=f"090100{i:04d}",
            status=StudentStatus.APPLICANT,
        )

    # --- Assignments: reserve + activate a few residents ---
    active_students = students[:6]
    free_beds = list(Bed.objects.filter(status=BedStatus.AVAILABLE))
    for idx, s in enumerate(active_students):
        bed = free_beds[idx]
        assignment = reserve_bed(s, bed, admin, reason="demo seed")
        activate_assignment(assignment, admin, condition_summary="Move-in inspection OK")
        generate_initial_invoice(s, assignment)

    # Reserve one more (reserved status for the dashboard)
    s = students[6]
    bed = free_beds[6]
    reserve_bed(s, bed, admin, reason="demo seed - pending payment")

    # One checked-out student with history
    s = students[7]
    bed = free_beds[7]
    assignment = reserve_bed(s, bed, admin)
    activate_assignment(assignment, admin)
    Invoice.objects.filter(student=s).update(status=InvoiceStatus.PAID)
    Assignment.objects.filter(pk=assignment.pk).update(status=AssignmentStatus.COMPLETED)
    Bed.objects.filter(pk=bed.pk).update(status=BedStatus.AVAILABLE)
    Student.objects.filter(pk=s.pk).update(status=StudentStatus.CHECKED_OUT)

    # A suspended student
    students[8].status = StudentStatus.SUSPENDED
    students[8].save(update_fields=["status"])

    # --- Payments: one pending review, one confirmed, one rejected ---
    pending_inv = active_students[0].invoices.first()
    if pending_inv:
        p = Payment.objects.create(
            invoice=pending_inv,
            student=active_students[0],
            amount=pending_inv.total_amount(),
            status=PaymentStatus.PENDING_REVIEW,
            method=PaymentMethod.BANK_TRANSFER,
        )
        PaymentEvidence.objects.create(
            payment=p, source="student_portal", file="seed/bank-transfer-demo.png"
        )

    if active_students[1].invoices.first():
        inv = active_students[1].invoices.first()
        Payment.objects.create(
            invoice=inv, student=active_students[1], amount=inv.total_amount(),
            status=PaymentStatus.REJECTED, reviewed_by=finance,
            review_note="Duplicate transfer detected", method=PaymentMethod.BANK_TRANSFER,
        )

    # Push a couple of invoices overdue
    Invoice.objects.filter(student=active_students[2]).update(
        due_date=date.today() - timedelta(days=5)
    )
    Invoice.objects.filter(student=active_students[3]).update(
        due_date=date.today() - timedelta(days=10)
    )
    mark_overdue_invoices()

    # --- Announcements ---
    Announcement.objects.create(
        title="Welcome to the dormitory portal",
        body="Please complete your profile and upload payment evidence for issued invoices.",
        audience=Audience.ALL,
        created_by=admin,
    )
    Announcement.objects.create(
        title="Fire drill scheduled",
        body="A mandatory fire drill will take place this Saturday at 8:00 AM.",
        audience=Audience.STUDENTS,
        created_by=admin,
    )

    print(
        "Seed complete: "
        f"{Student.objects.count()} students, "
        f"{Bed.objects.count()} beds, "
        f"{Assignment.objects.count()} assignments, "
        f"{Invoice.objects.count()} invoices, "
        f"{Payment.objects.count()} payments."
    )
