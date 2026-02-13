# antrean/decorators.py

from functools import wraps
from django.shortcuts import redirect

def mahasiswa_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get("mahasiswa_id"):
            return redirect("antrean:login_mahasiswa")
        return view_func(request, *args, **kwargs)
    return wrapper
