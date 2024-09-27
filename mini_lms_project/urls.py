"""
URL configuration for mini_lms_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import path, include
from lms_app.views import TeacherSignUpView, StudentSignUpView, TeacherLoginView, StudentLoginView, logout_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/teacher/', TeacherSignUpView.as_view(), name='teacher_signup'),
    path('accounts/signup/student/', StudentSignUpView.as_view(), name='student_signup'),
    path('accounts/login/teacher/', TeacherLoginView.as_view(), name='teacher_login'),
    path('accounts/login/student/', StudentLoginView.as_view(), name='student_login'),
    # path('accounts/logout/', logout_view, name='logout'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

    
    path('', include('lms_app.urls')),
]
