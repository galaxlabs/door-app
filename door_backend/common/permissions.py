from rest_framework.permissions import BasePermission


class IsOrganizationAdmin(BasePermission):
    """Allow access only to org admins."""

    def has_object_permission(self, request, view, obj):
        org = getattr(obj, "organization", obj)
        return org.members.filter(user=request.user, role="admin").exists()


class IsOrganizationMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        org = getattr(obj, "organization", obj)
        return org.members.filter(user=request.user).exists()
