from rest_framework import permissions


class ApiPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Postman: users/users_bad_requests/users_me // No Auth
        if view.action == "me":
            return request.user.is_authenticated
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            # or obj.author == request.user
        )
