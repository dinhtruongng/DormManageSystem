"""Resident views: student list/search, import, profile detail, student self-portal."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from dorm_system.accounts.permissions import can_view_student, role_required
from dorm_system.common.models import Role, StudentStatus
from dorm_system.residents.models import Student
from dorm_system.residents.services import import_students


@role_required(Role.ADMIN, Role.FINANCE, Role.SYSADMIN)
def student_list(request):
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    students = Student.objects.all()
    if q:
        students = students.filter(full_name__icontains=q) | students.filter(
            student_code__icontains=q
        )
    if status:
        students = students.filter(status=status)
    students = students.distinct()
    return render(
        request,
        "residents/student_list.html",
        {"students": students, "q": q, "status": status, "statuses": StudentStatus.choices},
    )


@role_required(Role.ADMIN, Role.FINANCE, Role.SYSADMIN)
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(
        request,
        "residents/student_detail.html",
        {
            "student": student,
            "assignment": student.active_assignment(),
            "invoices": student.invoices.all(),
            "payments": student.payments.all(),
            "history": student.assignments.all(),
        },
    )


@role_required(Role.ADMIN, Role.SYSADMIN)
def student_import(request):
    """Bulk-import students from a CSV upload (FR-02, §9.2)."""
    if request.method == "POST":
        uploaded = request.FILES.get("csv")
        if uploaded is None:
            messages.error(request, "Please choose a CSV file to upload.")
        else:
            try:
                result = import_students(uploaded)
            except UnicodeDecodeError:
                messages.error(request, "File must be UTF-8 encoded text.")
            else:
                messages.success(
                    request,
                    f"Imported {result.created} student(s); "
                    f"{result.skipped} skipped; {len(result.errors)} issue(s).",
                )
                for note in result.errors[:10]:
                    messages.warning(request, note)
            return redirect("residents:student_list")
    return render(request, "residents/student_import.html")


@login_required(login_url="/auth/login/")
def me(request):
    """Student self-portal: profile, assignment, invoices, announcements."""
    student = getattr(request.user, "student", None)
    if student is None:
        # Non-student user hitting the student landing; bounce home.
        return redirect("/")
    assignment = student.active_assignment()
    announcements = _visible_announcements(student)
    return render(
        request,
        "residents/student_portal.html",
        {
            "student": student,
            "assignment": assignment,
            "invoices": student.invoices.all(),
            "balance": student.balance_due(),
            "announcements": announcements,
        },
    )


def _visible_announcements(student):
    from dorm_system.common.models import Audience
    from dorm_system.communications.models import Announcement

    return Announcement.objects.filter(audience__in=(Audience.ALL, Audience.STUDENTS))[:5]
