from django.conf import settings
from rest_framework.permissions import BasePermission


class InternalServiceTokenPermission(BasePermission):
    message = "Invalid or missing internal service token."

    def has_permission(self, request, view):
        configured_token = (settings.INTERNAL_SERVICE_TOKEN or "").strip()
        if not configured_token:
            return False

        request_token = request.headers.get("X-Service-Token", "").strip()
        return bool(request_token) and request_token == configured_token
