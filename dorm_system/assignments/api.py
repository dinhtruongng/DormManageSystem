from django.views.decorators.http import require_POST

from dorm_system.assignments.models import Assignment
from dorm_system.assignments.services import (
    AssignmentConflict,
    activate_assignment,
    recommend_beds,
    reserve_bed,
    settle_checkout,
)
from dorm_system.billing.services import generate_initial_invoice
from dorm_system.common.api import api_fail, api_ok, read_json
from dorm_system.residents.models import Student
from dorm_system.rooms.models import Bed


def recommendations(request):
    body, err = read_json(request)
    if err:
        return api_fail("Invalid JSON body.", status=400)
    try:
        student = Student.objects.get(pk=body.get("studentId"))
    except Student.DoesNotExist:
        return api_fail("Student not found.", status=404)
    prefs = body.get("preferences") or {}
    limit = body.get("limit", 5)
    cands = recommend_beds(student, prefs, limit=limit)
    return api_ok(
        "Recommendations generated.",
        {
            "studentId": student.id,
            "candidates": [c.__dict__ for c in cands],
        },
    )


def assignment_create(request):
    body, err = read_json(request)
    if err:
        return api_fail("Invalid JSON body.", status=400)
    try:
        student = Student.objects.get(pk=body.get("studentId"))
        bed = Bed.objects.get(pk=body.get("bedId"))
        assignment = reserve_bed(student, bed, request.user)
        generate_initial_invoice(student, assignment)
    except AssignmentConflict as exc:
        return api_fail(str(exc), status=409)
    except (Student.DoesNotExist, Bed.DoesNotExist):
        return api_fail("Student or bed not found.", status=404)
    return api_ok("Assignment reserved.", {"assignmentId": assignment.id}, )


def check_in(request, assignment_id):
    try:
        assignment = Assignment.objects.get(pk=assignment_id)
        activate_assignment(assignment, request.user)
    except AssignmentConflict as exc:
        return api_fail(str(exc), status=409)
    return api_ok("Check-in complete.", {"assignmentId": assignment.id})


def check_out(request, assignment_id):
    body, _ = read_json(request)
    try:
        assignment = Assignment.objects.get(pk=assignment_id)
        settle_checkout(
            assignment,
            request.user,
            damage_fee=float((body or {}).get("damageFee", 0) or 0),
            needs_cleaning=bool((body or {}).get("needsCleaning")),
            notes=(body or {}).get("notes", ""),
        )
    except AssignmentConflict as exc:
        return api_fail(str(exc), status=409)
    return api_ok("Check-out settled.", {"assignmentId": assignment.id})
