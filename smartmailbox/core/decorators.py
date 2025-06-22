from django.shortcuts import redirect
from functools import wraps

def activation_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            if hasattr(request.user, 'userprofile') and not request.user.userprofile.activated:
                return redirect('activate_account')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
