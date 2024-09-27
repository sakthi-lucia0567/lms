from django.views.generic import CreateView
from .forms import TeacherSignUpForm, StudentSignUpForm
from .models import User
from django.forms import formset_factory
import requests
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Quiz, Question, Answer, QuizSubmission
from .forms import CourseForm, QuizForm, QuestionForm, AnswerFormSet
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .forms import CustomLoginForm

# ... rest of your views code ...


class TeacherSignUpView(CreateView):
    model = User
    form_class = TeacherSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'teacher'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Teacher Registered successfully!")
        return redirect('teacher_dashboard')

class StudentSignUpView(CreateView):
    model = User
    form_class = StudentSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'student'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Student Registered successfully!")
        return redirect('student_dashboard')

class TeacherLoginView(LoginView):
    template_name = 'registration/login_teacher.html'
    authentication_form = CustomLoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()
        if user.is_teacher:
            login(self.request, user)
            messages.success(self.request, "Logged in successfully!")
            return redirect('teacher_dashboard')
        else:
            messages.error(self.request, "You are not authorized as a teacher.")
            return redirect('teacher_login')


class StudentLoginView(LoginView):
    template_name = 'registration/login_student.html'
    authentication_form = CustomLoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()
        if user.is_student:
            login(self.request, user)
            messages.success(self.request, "Logged in successfully!")
            return redirect('student_dashboard')
        else:
            messages.error(self.request, "You are not authorized as a student.")
            return redirect('student_login')


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, "Logged out successfully!")
        return redirect('home')  # Redirect to the URL pattern 'home'
    return redirect('home')  # Fallback redirect to 'home'


def home(request):
    return render(request, 'lms_app/home.html')

@login_required
def teacher_dashboard(request):
    if not request.user.is_teacher:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    courses = Course.objects.filter(teacher=request.user)
    return render(request, 'lms_app/teacher_dashboard.html', {'courses': courses})

@login_required
def student_dashboard(request):
    if not request.user.is_student:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    enrolled_courses = request.user.enrolled_courses.all()
    available_courses = Course.objects.exclude(students=request.user)
    
    return render(request, 'lms_app/student_dashboard.html', {
        'enrolled_courses': enrolled_courses,
        'available_courses': available_courses
    })

@login_required
def create_course(request):
    if not request.user.is_teacher:
        messages.error(request, "You don't have permission to create a course.")
        return redirect('home')
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            messages.success(request, 'Course created successfully.')
            return redirect('teacher_dashboard')
    else:
        form = CourseForm()
    return render(request, 'lms_app/create_course.html', {'form': form})

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.user.is_teacher and course.teacher != request.user:
        messages.error(request, "You don't have permission to view this course.")
        return redirect('teacher_dashboard')
    if request.user.is_student and request.user not in course.students.all():
        messages.error(request, "You are not enrolled in this course.")
        return redirect('student_dashboard')
    return render(request, 'lms_app/course_detail.html', {'course': course})

@login_required
def create_quiz(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if not request.user.is_teacher or course.teacher != request.user:
        messages.error(request, "You don't have permission to create a quiz for this course.")
        return redirect('teacher_dashboard')
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.course = course
            quiz.save()
            messages.success(request, 'Quiz created successfully.')
            return redirect('course_detail', course_id=course.id)
    else:
        form = QuizForm()
    return render(request, 'lms_app/create_quiz.html', {'form': form, 'course': course})

@login_required
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.user.is_teacher and quiz.course.teacher != request.user:
        messages.error(request, "You don't have permission to view this quiz.")
        return redirect('teacher_dashboard')
    if request.user.is_student and request.user not in quiz.course.students.all():
        messages.error(request, "You are not enrolled in the course for this quiz.")
        return redirect('student_dashboard')
    return render(request, 'lms_app/quiz_detail.html', {'quiz': quiz})

@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if not request.user.is_student or request.user not in quiz.course.students.all():
        messages.error(request, "You don't have permission to take this quiz.")
        return redirect('student_dashboard')
    # Implement quiz-taking logic here
    return render(request, 'lms_app/take_quiz.html', {'quiz': quiz})


@login_required
def create_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        answer_formset = AnswerFormSet(request.POST)
        if question_form.is_valid() and answer_formset.is_valid():
            question = question_form.save(commit=False)
            question.quiz = quiz
            question.save()
            answer_formset.instance = question
            answer_formset.save()
            messages.success(request, 'Question added successfully.')
            return redirect('quiz_detail', quiz_id=quiz.id)
    else:
        question_form = QuestionForm()
        answer_formset = AnswerFormSet()
    return render(request, 'lms_app/create_question.html', {
        'question_form': question_form,
        'answer_formset': answer_formset,
        'quiz': quiz
    })

# @login_required
# def take_quiz(request, quiz_id):
#     quiz = get_object_or_404(Quiz, id=quiz_id)
#     if not request.user.is_student or request.user not in quiz.course.students.all():
#         messages.error(request, "You don't have permission to take this quiz.")
#         return redirect('student_dashboard')
    
#     if request.method == 'POST':
#         score = 0
#         total_questions = quiz.questions.count()
#         for question in quiz.questions.all():
#             selected_answer_id = request.POST.get(f'question_{question.id}')
#             if selected_answer_id:
#                 selected_answer = Answer.objects.get(id=selected_answer_id)
#                 if selected_answer.is_correct:
#                     score += 1
        
#         percentage_score = (score / total_questions) * 100
#         QuizSubmission.objects.create(student=request.user, quiz=quiz, score=percentage_score)
#         messages.success(request, f'Quiz submitted successfully. Your score: {percentage_score:.2f}%')
#         return redirect('student_dashboard')
    
#     questions = quiz.questions.all()
#     return render(request, 'lms_app/take_quiz.html', {'quiz': quiz, 'questions': questions})

@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.user not in quiz.course.students.all():
        messages.error(request, "You are not enrolled in the course for this quiz.")
        return redirect('student_dashboard')
    
    if request.method == 'POST':
        score = 0
        total_questions = quiz.questions.count()
        for question in quiz.questions.all():
            selected_answer_id = request.POST.get(f'question_{question.id}')
            if selected_answer_id:
                selected_answer = Answer.objects.get(id=selected_answer_id)
                if selected_answer.is_correct:
                    score += 1
        
        percentage_score = (score / total_questions) * 100
        QuizSubmission.objects.create(student=request.user, quiz=quiz, score=percentage_score)
        messages.success(request, f'Quiz submitted successfully. Your score: {percentage_score:.2f}%')
        return redirect('student_course_detail', course_id=quiz.course.id)
    
    questions = quiz.questions.all()
    return render(request, 'lms_app/take_quiz.html', {'quiz': quiz, 'questions': questions})


def fetch_trivia_questions(amount=5, category=9, difficulty='medium'):
    url = f"https://opentdb.com/api.php?amount={amount}&category={category}&difficulty={difficulty}&type=multiple"
    response = requests.get(url)
    data = response.json()
    return data['results']

@login_required
def create_api_quiz(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if not request.user.is_teacher or course.teacher != request.user:
        messages.error(request, "You don't have permission to create a quiz for this course.")
        return redirect('teacher_dashboard')
    
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.course = course
            quiz.save()
            
            # Fetch questions from API
            trivia_questions = fetch_trivia_questions()
            
            for trivia_question in trivia_questions:
                question = Question.objects.create(
                    quiz=quiz,
                    text=trivia_question['question'],
                    is_api_question=True
                )
                Answer.objects.create(
                    question=question,
                    text=trivia_question['correct_answer'],
                    is_correct=True
                )
                for incorrect_answer in trivia_question['incorrect_answers']:
                    Answer.objects.create(
                        question=question,
                        text=incorrect_answer,
                        is_correct=False
                    )
            
            messages.success(request, 'API Quiz created successfully.')
            return redirect('course_detail', course_id=course.id)
    else:
        form = QuizForm()
    return render(request, 'lms_app/create_api_quiz.html', {'form': form, 'course': course})


@login_required
def join_course(request, course_id):
    if not request.user.is_student:
        messages.error(request, "You don't have permission to join courses.")
        return redirect('home')
    
    course = get_object_or_404(Course, id=course_id)
    if request.user in course.students.all():
        messages.warning(request, "You are already enrolled in this course.")
    else:
        course.students.add(request.user)
        messages.success(request, f"You have successfully joined the course: {course.title}")
    
    return redirect('student_dashboard')


@login_required
def student_course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.user not in course.students.all():
        messages.error(request, "You are not enrolled in this course.")
        return redirect('student_dashboard')
    
    quizzes = Quiz.objects.filter(course=course)
    quiz_results = {result.quiz.id: result for result in QuizSubmission.objects.filter(student=request.user, quiz__course=course)}
    
    return render(request, 'lms_app/student_course_detail.html', {
        'course': course,
        'quizzes': quizzes,
        'quiz_results': quiz_results
    })



@login_required
def student_quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.user not in quiz.course.students.all():
        messages.error(request, "You are not enrolled in the course for this quiz.")
        return redirect('student_dashboard')
    
    submission = QuizSubmission.objects.filter(student=request.user, quiz=quiz).first()
    
    return render(request, 'lms_app/student_quiz_detail.html', {
        'quiz': quiz,
        'submission': submission
    })