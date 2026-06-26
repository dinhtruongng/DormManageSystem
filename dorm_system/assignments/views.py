"""Assignment workflow views: recommendation, reserve, check-in, check-out."""

from django.contrib import messages as django_messages
from django.shortcuts import get_object_or_404, redirect, render

from dorm_system.accounts.permissions import role_required
from dorm_system.assignments.models import Assignment
from dorm_system.assignments.services import (
    AssignmentConflict,
    activate_assignment,
    recommend_beds,
    reserve_bed,
    settle_checkout,
    transfer_student,
)
from dorm_system.billing.services import generate_initial_invoice
from dorm_system.common.models import Role
from dorm_system.residents.models import Student
from dorm_system.rooms.models import Bed


@role_required(Role.ADMIN)
def recommend(request, student_id):
    """Show ranked bed recommendations for a student (FR-04)."""
    student = get_object_or_404(Student, pk=student_id)
    prefs = {}
    if request.GET.get("building_id"):
        try:
            prefs["building_id"] = int(request.GET["building_id"])
        except ValueError:
            pass
    candidates = recommend_beds(student, prefs)
    return render(
        request,
        "assignments/recommend.html",
        {"student": student, "candidates": candidates},
    )


@role_required(Role.ADMIN)
def reserve(request, student_id, bed_id):
    student = get_object_or_404(Student, pk=student_id)
    bed = get_object_or_404(Bed, pk=bed_id)
    try:
        assignment = reserve_bed(student, bed, request.user, reason="manual reservation")
    except AssignmentConflict as exc:
        django_messages.error(request, str(exc))
        return redirect("assignments:recommend", student_id=student.id)
    generate_initial_invoice(student, assignment)
    django_messages.success(request, f"Reserved {bed} for {student.full_name}.")
    return redirect("assignments:detail", assignment_id=assignment.id)


@role_required(Role.ADMIN)
def detail(request, assignment_id):
    assignment = get_object_or_404(Assignment.objects.select_related("student", "bed__room__floor__building"), pk=assignment_id)
    return render(request, "assignments/detail.html", {"assignment": assignment})


@role_required(Role.ADMIN)
def check_in(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    try:
        activate_assignment(assignment, request.user)
        django_messages.success(request, "Check-in complete. Assignment is now active.")
    except AssignmentConflict as exc:
        django_messages.error(request, str(exc))
    return redirect("assignments:detail", assignment_id=assignment.id)


@role_required(Role.ADMIN)
def checkout_form(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    return render(request, "assignments/checkout_form.html", {"assignment": assignment})


@role_required(Role.ADMIN)
def settle(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    if request.method == "POST":
        try:
            damage_fee = float(request.POST.get("damage_fee", 0) or 0)
        except ValueError:
            damage_fee = 0
        try:
            settle_checkout(
                assignment,
                request.user,
                condition_summary=request.POST.get("condition_summary", ""),
                damage_fee=damage_fee,
                needs_cleaning=bool(request.POST.get("needs_cleaning")),
                notes=request.POST.get("notes", ""),
            )
            django_messages.success(request, "Check-out settled. Bed released to inventory.")
        except AssignmentConflict as exc:
            django_messages.error(request, str(exc))
    return redirect("assignments:detail", assignment_id=assignment.id)
