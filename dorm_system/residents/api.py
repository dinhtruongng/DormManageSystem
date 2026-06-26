from dorm_system.common.api import api_ok
from dorm_system.residents.models import Student


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
