from django.shortcuts import redirect
from django.contrib import messages

class RoleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if 'teacher' in request.path and not request.user.is_teacher:
                messages.error(request, "You don't have permission to access this page.")
                return redirect('home')
            elif 'student' in request.path and not request.user.is_student:
                messages.error(request, "You don't have permission to access this page.")
                return redirect('home')
        return self.get_response(request)