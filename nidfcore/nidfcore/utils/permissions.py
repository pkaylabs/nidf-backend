from rest_framework.permissions import BasePermission

from nidfcore.utils.constants import UserType


class IsSuperuser(BasePermission):
    """
    Allows access only to superusers.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser

class IsCentralAndSuperUser(BasePermission):
    """
    Allows access only to superusers and central management users.
    """
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and (user.is_superuser or user.user_type == UserType.FINANCE_OFFICER.value)
