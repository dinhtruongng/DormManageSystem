"""Role-based access helpers used by views and API endpoints.

Implements the IdentityService boundary from the report (Section 8.1):
require_role, get_profile, can_view_student.
"""

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from dorm_system.accounts.models import UserProfile, get_profile
from dorm_system.common.models import Role


def require_role(user, roles):
    """Raise PermissionDenied unless the user holds one of the allowed roles."""
    profile = get_profile(user)
    if profile is None or profile.role not in roles:
        raise PermissionDenied("Your role is not allowed to perform this action.")
    return profile


def can_view_student(user, student):
    """Enforce student self-access plus staff visibility (FR-02)."""
    profile = get_profile(user)
    if profile is None:
        return False
    if profile.role == Role.STUDENT:
        return student.user_id == user.id
    return profile.role in (Role.ADMIN, Role.FINANCE, Role.SYSADMIN)


def role_required(*roles):
    """View decorator combining login and role checks."""

    def decorator(view):
        @login_required(login_url="/auth/login/")
        @wraps(view)
        def _wrapped(request, *args, **kwargs):
            require_role(request.user, roles)
            return view(request, *args, **kwargs)

        return _wrapped

    return decorator


def home_redirect_for_role(profile):
    """Role-aware landing page (report Section 8.2)."""
    if profile is None:
        return "/auth/login/"
    if profile.role == Role.STUDENT:
        return "/residents/me/"
    if profile.role == Role.FINANCE:
        return "/payments/review/"
    return "/reports/dashboard/"


__all__ = [
    "UserProfile",
    "require_role",
    "can_view_student",
    "role_required",
    "home_redirect_for_role",
]
