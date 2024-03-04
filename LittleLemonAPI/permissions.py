from rest_framework import permissions 


class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Manager').exists()


class IsDeliveryCrew(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Delivery_crew').exists()


class IsManagerOrDeliveryCrew(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name__in=['Manager', 'Delivery_crew']).exists()
    

class IsManagerOrAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.groups.filter(name="Manager").exists() or request.user.is_superuser:
            return True 
        return False 
    

class IsManagerOrSelfOrDeliveryCrew(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in ('GET', 'POST'):
            # Allow authenticated users to perform GET and POST requests
            return request.user.is_authenticated
        else:
            # For other methods, restrict to the "Manager" group
            return request.user.groups.filter(name="Manager").exists()

    def has_object_permission(self, request, view, obj):
        if request.method == 'PATCH':
            # Allow access to both "Manager" and "Delivery_crew" for PATCH method
            return (
                request.user.groups.filter(name__in=["Manager", "Delivery_crew"]).exists() or
                request.user == obj.user  # Allow the owner to patch
            )
        else:
            # For other methods, restrict to the "Manager" group
            return request.user.groups.filter(name="Manager").exists()
