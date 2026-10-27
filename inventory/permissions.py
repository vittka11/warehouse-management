from rest_framework.permissions import BasePermission


class IsWarehouseManager(BasePermission):
    message = "Only Warehouse Managers can perform this action."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (
                request.user.is_superuser
                or request.user.groups.filter(
                    name="Warehouse Managers"
                ).exists()
            )
        )


class IsWarehouseStaffOrManager(BasePermission):
    message = "Only Warehouse Staff or Managers can view warehouse data."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (
                request.user.is_superuser
                or request.user.groups.filter(
                    name__in=["Warehouse Staff", "Warehouse Managers"]
                ).exists()
            )
        )