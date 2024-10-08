from rest_framework import permissions

class IsAuthorOrReadOnly(permissions.BasePermission): 
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:  #include safe methods such as get , head and options   
            return True
        return obj.user == request.user # only allow author to update or delete their own movie comments or movie reviews
    