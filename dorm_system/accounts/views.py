from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from dorm_system.accounts.forms import LoginForm
from dorm_system.accounts.models import get_profile
from dorm_system.accounts.permissions import home_redirect_for_role


def home(request):
    """Role-aware entry point: bounce to the right landing page or login."""
    profile = get_profile(request.user)
    if profile is None:
        return redirect("/auth/login/")
    return redirect(home_redirect_for_role(profile))


def login(request):
    if request.user.is_authenticated:
        return redirect(home_redirect_for_role(get_profile(request.user)))

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is None:
                form.add_error(None, "Invalid username or password.")
            else:
                auth_login(request, user)
                return redirect(home_redirect_for_role(get_profile(user)))
    else:
        form = LoginForm()
    return render(request, "accounts/login.html", {"form": form, "demo_logins": DEMO_LOGINS})


@login_required(login_url="/auth/login/")
def logout(request):
    auth_logout(request)
    return redirect("/auth/login/")


# Shown on the login page so a reviewer can pick a role instantly.
DEMO_LOGINS = [
    ("admin", "admin", "Admin"),
    ("finance", "finance", "Finance"),
    ("student01", "student", "Student (sample resident)"),
]
