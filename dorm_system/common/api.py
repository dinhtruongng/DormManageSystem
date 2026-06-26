"""Shared JSON envelope helpers (report Section 8.7: {success, message, data})."""

import json

from django.http import HttpResponse, JsonResponse


def api_ok(message, data=None):
    return JsonResponse({"success": True, "message": message, "data": data or {}})


def api_fail(message, *, status=400, errors=None):
    body = {"success": False, "message": message}
    if errors:
        body["errors"] = errors
    return JsonResponse(body, status=status)


def read_json(request):
    """Best-effort JSON body parser for POST endpoints."""
    try:
        return json.loads(request.body or b"{}"), None
    except json.JSONDecodeError as exc:
        return None, str(exc)
