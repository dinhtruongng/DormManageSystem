from dorm_system.accounts.models import get_profile


def role_context(request):
    """Expose the active user's profile + role to every template."""
    profile = get_profile(getattr(request, "user", None))
    return {
        "active_profile": profile,
        "active_role": profile.role if profile else None,
    }
