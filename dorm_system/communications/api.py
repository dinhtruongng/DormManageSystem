from django.contrib.auth import get_user_model

from dorm_system.accounts.models import UserProfile
from dorm_system.common.api import api_fail, api_ok, read_json
from dorm_system.common.models import Audience, Role
from dorm_system.communications.models import Announcement
from dorm_system.communications.services import send_announcement

User = get_user_model()


def announcement_create(request):
    body, err = read_json(request)
    if err:
        return api_fail("Invalid JSON body.", status=400)
    title = (body or {}).get("title")
    if not title:
        return api_fail("title is required.", status=422)
    ann = Announcement.objects.create(
        title=title,
        body=(body or {}).get("body", ""),
        audience=(body or {}).get("audience", Audience.ALL),
        created_by=request.user,
    )
    send_announcement(ann, _recipients_for(ann.audience))
    return api_ok("Announcement created.", {"announcementId": ann.id})


def _recipients_for(audience):
    profiles = UserProfile.objects.select_related("user")
    if audience == Audience.STUDENTS:
        profiles = profiles.filter(role=Role.STUDENT)
    elif audience == Audience.STAFF:
        profiles = profiles.filter(role__in=(Role.ADMIN, Role.FINANCE, Role.SYSADMIN))
    return [p.user for p in profiles if p.user_id]
