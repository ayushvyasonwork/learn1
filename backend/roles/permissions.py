from rest_framework.permissions import BasePermission
from .models import GroupUserRole
from rest_framework import permissions

class HasGroupPermission(BasePermission):
    def has_permission(self, request, view):
        group_id = request.data.get('group') or request.query_params.get('group')
        user = request.user

        if not group_id or not user.is_authenticated:
            return False

        # Check if user has at least one role in this group
        return GroupUserRole.objects.filter(user=user, group_id=group_id).exists()

class IsOrgAdmin(permissions.BasePermission):
    """
    Custom permission to allow only organization admins to create permissions.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_org_admin)