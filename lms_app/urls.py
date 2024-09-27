from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),  
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('course/create/', views.create_course, name='create_course'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('quiz/create/<int:course_id>/', views.create_quiz, name='create_quiz'),
    path('quiz/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('quiz/<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    path('course/<int:course_id>/create-api-quiz/', views.create_api_quiz, name='create_api_quiz'),
    path('quiz/<int:quiz_id>/create-question/', views.create_question, name='create_question'),
    path('student/join-course/<int:course_id>/', views.join_course, name='join_course'),
    path('student/course/<int:course_id>/', views.student_course_detail, name='student_course_detail'),
    path('student/quiz/<int:quiz_id>/', views.student_quiz_detail, name='student_quiz_detail'),
    path('student/quiz/<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

]