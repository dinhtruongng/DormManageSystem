"""AssignmentService + CheckoutService (report Section 8.1).

Implements the assignment scoring strategy, transactional bed reservation with
a row lock (NFR-02), check-in activation, transfer, and check-out settlement.
"""

from dataclasses import dataclass
from datetime import date

from django.db import transaction

from dorm_system.assignments.models import Assignment, Inspection
from dorm_system.billing.services import generate_initial_invoice
from dorm_system.common.models import (
    AssignmentStatus,
    AuditLog,
    BedStatus,
    InspectionType,
    InvoiceItemType,
    RoomStatus,
    StudentStatus,
    record_audit,
)
from dorm_system.rooms.models import Bed


@dataclass
class AssignmentCandidate:
    bed_id: int
    building: str
    room: str
    bed_code: str
    available_beds_in_room: int
    policy_match: bool
    score: int
    reasons: list


class AssignmentScorer:
    """Strategy: score available beds by policy + capacity + preferences.

    Kept as a class so preference-based or roommate-matching scorers can be
    dropped in later (report Section 6.2, Strategy pattern).
    """

    def __init__(self, preferences=None):
        self.preferences = preferences or {}

    def score(self, candidate_bed, student):
        room = candidate_bed.room
        reasons = []
        score = 0

        if room.gender_policy in ("mixed", "unspecified"):
            score += 15
            reasons.append("mixed/unspecified room")
        elif room.gender_policy == student.gender:
            score += 40
            reasons.append("gender policy match")
        else:
            return None  # incompatible room

        available = room.available_bed_count()
        # Prefer rooms with more free beds (less crowded).
        if available >= 2:
            score += 10
            reasons.append(f"{available} beds free")

        pref_building = self.preferences.get("building_id")
        if pref_building and room.floor.building_id == pref_building:
            score += 20
            reasons.append("preferred building")

        if room.status == RoomStatus.MAINTENANCE:
            return None
        if candidate_bed.status != BedStatus.AVAILABLE:
            return None

        return score, reasons


def recommend_beds(student, preferences=None, limit=5):
    """Return ranked AssignmentCandidates (report pseudocode)."""
    scorer = AssignmentScorer(preferences or {})
    candidates = []
    for bed in Bed.objects.select_related("room__floor__building").filter(
        status=BedStatus.AVAILABLE, room__status=RoomStatus.OPEN
    ):
        result = scorer.score(bed, student)
        if result is None:
            continue
        score, reasons = result
        candidates.append(
            AssignmentCandidate(
                bed_id=bed.id,
                building=bed.room.floor.building.name,
                room=bed.room.room_number,
                bed_code=bed.bed_code,
                available_beds_in_room=bed.room.available_bed_count(),
                policy_match=True,
                score=score,
                reasons=reasons,
            )
        )
    candidates.sort(
        key=lambda c: (-c.score, c.building, c.room, c.bed_code)
    )
    return candidates[:limit]


class AssignmentConflict(Exception):
    pass


@transaction.atomic
def reserve_bed(student, bed, actor, reason=""):
    """Reserve a bed in a transaction, locking the row (FR-04, NFR-02)."""
    bed = Bed.objects.select_for_update().get(pk=bed.pk)
    if bed.status != BedStatus.AVAILABLE:
        raise AssignmentConflict("Bed is not available for reservation.")

    existing = Assignment.objects.filter(
        student=student, status__in=(AssignmentStatus.RESERVED, AssignmentStatus.ACTIVE)
    ).first()
    if existing:
        existing.status = AssignmentStatus.CANCELLED
        existing.save(update_fields=["status"])

    assignment = Assignment.objects.create(
        student=student,
        bed=bed,
        assigned_by=actor,
        status=AssignmentStatus.RESERVED,
        start_date=date.today(),
        reason=reason or "automatic reservation",
    )
    bed.status = BedStatus.RESERVED
    bed.save(update_fields=["status"])

    if student.status == StudentStatus.APPLICANT:
        student.status = StudentStatus.APPLICANT  # stays applicant until check-in
        student.save(update_fields=["status"])

    record_audit(
        actor, "reserve_bed", "bed", bed.id,
        new_value={"status": bed.status, "assignment": assignment.id}, reason=reason,
    )
    return assignment


@transaction.atomic
def activate_assignment(assignment, actor, condition_summary=""):
    """Finalize check-in: assignment active, bed occupied, student active."""
    assignment = Assignment.objects.select_for_update().get(pk=assignment.pk)
    bed = Bed.objects.select_for_update().get(pk=assignment.bed_id)
    if assignment.status != AssignmentStatus.RESERVED:
        raise AssignmentConflict("Only reserved assignments can be activated.")
    Inspection.objects.create(
        assignment=assignment,
        inspected_by=actor,
        type=InspectionType.CHECKIN,
        condition_summary=condition_summary or "Room handed over in good condition.",
    )
    assignment.status = AssignmentStatus.ACTIVE
    assignment.save(update_fields=["status"])
    bed.status = BedStatus.OCCUPIED
    bed.save(update_fields=["status"])
    assignment.student.status = StudentStatus.ACTIVE
    assignment.student.save(update_fields=["status"])
    record_audit(
        actor, "check_in", "assignment", assignment.id,
        new_value={"status": assignment.status, "bed": bed.status},
    )
    return assignment


@transaction.atomic
def transfer_student(assignment, new_bed, actor, reason=""):
    """Transfer: mark old assignment transferred, reserve new bed (FR-05)."""
    assignment = Assignment.objects.select_for_update().get(pk=assignment.pk)
    assignment.status = AssignmentStatus.TRANSFERRED
    assignment.end_date = date.today()
    assignment.save(update_fields=["status", "end_date"])
    old_bed = Bed.objects.get(pk=assignment.bed_id)
    old_bed.status = BedStatus.AVAILABLE
    old_bed.save(update_fields=["status"])
    record_audit(
        actor, "transfer_out", "assignment", assignment.id,
        new_value={"new_bed": new_bed.id}, reason=reason,
    )
    return reserve_bed(assignment.student, new_bed, actor, reason=reason or "transfer")


@transaction.atomic
def settle_checkout(
    assignment,
    actor,
    *,
    condition_summary="",
    damage_fee=0,
    needs_cleaning=False,
    notes="",
):
    """Check-out settlement (report Section 8.7 pseudocode)."""
    assignment = Assignment.objects.select_for_update().get(pk=assignment.pk)
    bed = Bed.objects.select_for_update().get(pk=assignment.bed_id)
    if assignment.status != AssignmentStatus.ACTIVE:
        raise AssignmentConflict("Only active assignments can be checked out.")

    inspection = Inspection.objects.create(
        assignment=assignment,
        inspected_by=actor,
        type=InspectionType.CHECKOUT,
        condition_summary=condition_summary,
        damage_fee=damage_fee,
        needs_cleaning=needs_cleaning,
        notes=notes,
    )

    if damage_fee and damage_fee > 0:
        from dorm_system.billing.services import generate_invoice
        from dorm_system.residents.models import Student

        penalty_invoice = generate_invoice(
            assignment.student,
            [
                {
                    "item_type": InvoiceItemType.PENALTY,
                    "description": "Checkout damage fee",
                    "amount": damage_fee,
                    "unit_price": damage_fee,
                }
            ],
        )

    assignment.status = AssignmentStatus.COMPLETED
    assignment.end_date = date.today()
    assignment.save(update_fields=["status", "end_date"])

    bed.status = BedStatus.CLEANING if needs_cleaning else BedStatus.AVAILABLE
    bed.save(update_fields=["status"])

    assignment.student.status = StudentStatus.CHECKED_OUT
    assignment.student.save(update_fields=["status"])

    record_audit(
        actor, "settle_checkout", "assignment", assignment.id,
        new_value={
            "status": assignment.status,
            "bed_status": bed.status,
            "damage_fee": str(damage_fee),
        },
        reason=notes,
    )
    return inspection
