from rest_framework import permissions

list_permissions = {
    'view_get_post_loans': {
        'GET': 3,
        'POST': 3,
        'PATCH': [0,2]
    },
    'view_get_update_loan': {
        'GET': 3,
        'PATCH': [0,2]
    },
    'view_get_update_delete_user': {
        'GET': 3,
        'PATCH': 3,
        'DELETE': 0
    },
    'view_get_post_users': {
        'POST': 0,
        'GET': 2,
        'PATCH': [0,2]
    },
    'view_get_post_years': {
        'GET': 3,
        'POST': 1
    },
    'view_get_post_activities': {
        'GET': 3,
        'POST': 1
    },
    'view_get_patch_delete_activity': {
        'GET': 3,
        'PATCH': 1,
        'DELETE': 1
    },
    'view_loan_apps': {
        'POST': 3
    },
    'view_logout': {
        'POST': 3
    },
    'view_notification_subscribe': {
        'POST': 3
    },
    'view_notification_unsubscribe': {
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