from functools import wraps
from flask_login import current_user
from flask import abort
from .models import Permission


# for cases when the entire view function needs to be available only to users with certain permissions
def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    return permission_required(Permission.ADMIN)(f)
