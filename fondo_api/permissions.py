from rest_framework import permissions

list_permissions = {
    'LoanView': {
        'GET': 3,
        'POST': 3,
        'PATCH': [0,2]
    },
    'LoanDetailView': {
        'GET': 3,
        'PATCH': [0,2]
    },
    'UserDetailView': {
        'GET': 3,
        'PATCH': 3,
        'DELETE': 0
    },
    'UserView': {
        'POST': 0,
        'GET': 2,
        'PATCH': [0,2]
    },
    'ActivityYearView': {
        'GET': 3,
        'POST': 1
    },
    'ActivityYearDetailView': {
        'GET': 3,
        'POST': 1
    },
    'ActivityDetailView': {
        'GET': 3,
        'PATCH': 1,
        'DELETE': 1
    },
    'LoanAppsView': {
        'POST': 3
    },
    'NotificationView': {
        'POST': 3
    }
}

class APIRolePermission(permissions.BasePermission):
    
    def has_permission(self, request, view):
        view_name = view.__class__.__name__
        method = request.method
        try:
            allowed_roles = list_permissions[view_name][method]
            if isinstance(allowed_roles, list):
                return request.user.userprofile.role in allowed_roles
            return request.user.userprofile.role <= allowed_roles
        except:
            return False