from rest_framework.permissions import BasePermission
from rest_framework.exceptions import NotAuthenticated

from .models import RolePermission


class AccessRulePermission(BasePermission):
    method_action_map = {
        "GET": "read",
        "POST": "create",
        "PUT": "update",
        "PATCH": "update",
        "DELETE": "delete",
    }

    def has_permission(self, request, view):
        resource_code = getattr(view, "access_resource", None)
        if not resource_code:
            return True

        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated("Authentication required")

        action_code = getattr(view, "access_action", None) or self.method_action_map.get(request.method)
        if not action_code:
            return True

        role_ids = request.user.user_roles.values_list("role_id", flat=True)
        if not role_ids:
            return False

        return RolePermission.objects.filter(
            role_id__in=role_ids,
            resource__code=resource_code,
            action__code=action_code,
            allow=True,
        ).exists()
