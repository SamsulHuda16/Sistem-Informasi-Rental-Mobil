from django.shortcuts import redirect
from functools import wraps

def pelanggan_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect('/admin/login/')

        if request.user.role != 'pelanggan':
            return redirect('/')

        return view_func(request, *args, **kwargs)

    return wrapper