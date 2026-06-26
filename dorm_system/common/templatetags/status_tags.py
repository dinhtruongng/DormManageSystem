"""Template helpers: status badges and message-tag mapping."""

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

# Map a raw status string to a Bootstrap badge color.
STATUS_COLORS = {
    # Bed / room
    "available": "success",
    "reserved": "warning",
    "occupied": "primary",
    "cleaning": "info",
    "maintenance": "info",
    "inactive": "secondary",
    "open": "success",
    "full": "warning",
    # Student
    "applicant": "secondary",
    "active": "success",
    "checked_out": "secondary",
    "suspended": "danger",
    # Invoice
    "draft": "secondary",
    "issued": "primary",
    "partially_paid": "warning",
    "paid": "success",
    "overdue": "danger",
    "cancelled": "secondary",
    # Payment
    "pending_review": "warning",
    "confirmed": "success",
    "rejected": "danger",
    "voided": "secondary",
    # Assignment
    "transferred": "info",
    "completed": "secondary",
}

MESSAGE_COLORS = {
    "error": "danger",
    "debug": "secondary",
    "warning": "warning",
    "success": "success",
    "info": "info",
}


@register.filter
def status_badge(value):
    """Render a coloured badge for a status enum value."""
    if not value:
        return ""
    color = STATUS_COLORS.get(value, "secondary")
    label = str(value).replace("_", " ").title()
    return mark_safe(f'<span class="badge text-bg-{color}">{label}</span>')


@register.filter(name="message_color")
def message_color(tag):
    return MESSAGE_COLORS.get(tag, "info")


@register.filter
def vnd(amount):
    """Format an amount in VND."""
    try:
        return f"{float(amount):,.0f} VND"
    except (TypeError, ValueError):
        return amount
