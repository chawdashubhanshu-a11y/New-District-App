from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def organization_required(view):
    @login_required
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        is_org = request.user.groups.filter(name="Organization").exists()
        if not is_org or not hasattr(request.user, "organization_profile"):
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return wrapper