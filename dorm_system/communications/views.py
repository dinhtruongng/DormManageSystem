"""Communication views: announcements list and create form."""

from django.contrib import messages as django_messages
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render

from dorm_system.accounts.models import UserProfile
from dorm_system.accounts.permissions import role_required
from dorm_system.common.models import Audience, Role
from dorm_system.communications.forms import AnnouncementForm
from dorm_system.communications.models import Announcement
from dorm_system.communications.services import send_announcement

User = get_user_model()


@role_required(Role.ADMIN)
def announcement_list(request):
    items = Announcement.objects.all()
    return render(request, "communications/announcement_list.html", {"announcements": items})


@role_required(Role.ADMIN)
def announcement_create(request):
    if request.method == "POST":
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            ann = Announcement.objects.create(
                title=form.cleaned_data["title"],
                body=form.cleaned_data["body"],
                audience=form.cleaned_data["audience"],
                created_by=request.user,
            )
            recipients = _recipients_for(form.cleaned_data["audience"])
            send_announcement(ann, recipients)
            django_messages.success(request, "Announcement published and notifications queued.")
            return redirect("communications:list")
    else:
        form = AnnouncementForm()
    return render(request, "communications/announcement_form.html", {"form": form})


def _recipients_for(audience):
    profiles = UserProfile.objects.select_related("user")
    if audience == Audience.STUDENTS:
        profiles = profiles.filter(role=Role.STUDENT)
    elif audience == Audience.STAFF:
        profiles = profiles.filter(role__in=(Role.ADMIN, Role.FINANCE, Role.SYSADMIN))
    return [p.user for p in profiles if p.user_id]
