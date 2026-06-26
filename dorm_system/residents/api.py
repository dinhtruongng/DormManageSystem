from dorm_system.accounts.permissions import require_role
from dorm_system.common.api import api_fail, api_ok, read_json
from dorm_system.common.models import Role
from dorm_system.residents.models import Student
from dorm_system.residents.services import create_student


def student_list(request):
    rows = [
        {
            "studentId": s.id,
            "studentCode": s.student_code,
            "fullName": s.full_name,
            "status": s.status,
        }
        for s in Student.objects.all()[:100]
    ]
    return api_ok("Student list.", {"students": rows})


def student_create(request):
    """Create a student record (§8.7, FR-02). Admin/SYSADMIN only."""
    require_role(request.user, (Role.ADMIN, Role.SYSADMIN))  # raises -> 403 otherwise
    body, err = read_json(request)
    if err:
        return api_fail("Invalid JSON body.", status=400)
    required = ("studentCode", "fullName")
    if not all(body.get(k) for k in required):
        return api_fail("studentCode and fullName are required.", status=400)
    try:
        student = create_student(
            {
                "student_code": body["studentCode"],
                "full_name": body["fullName"],
                "gender": body.get("gender", "other"),
                "email": body.get("email", ""),
                "phone": body.get("phone", ""),
            }
        )
    except ValueError as exc:
        return api_fail(str(exc), status=409)
    resp = api_ok(
        "Student created.",
        {
            "studentId": student.id,
            "studentCode": student.student_code,
            "fullName": student.full_name,
        },
    )
    resp.status_code = 201
    return resp
