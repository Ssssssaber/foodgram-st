from rest_framework import permissions


class ApiPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == "me":
            return request.user.is_authenticated
        else:
            return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
        )
