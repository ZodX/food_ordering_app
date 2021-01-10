from django.http import HttpResponse
from django.shortcuts import redirect

def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper_func

def allowed_users(allower_roles = []):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            user_groups = set([element.name for element in request.user.groups.all()])
            allowed_groups = set(allower_roles)

            if len(user_groups.intersection(allowed_groups)) > 0:
                return view_func(request, *args, **kwargs)
            
            return HttpResponse('You are not authorized to view this page.')
        return wrapper_func
    return decorator

def admin_only(view_func):
    def wrapper_func(request, *args, **kwargs):
        group = None
        if request.user.groups.exists():
            group = request.user.groups.all()[0].name

        if group == 'admin':
            return view_func(request, *args, **kwargs)

        return redirect('home')

    return wrapper_func