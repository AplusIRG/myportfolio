# D:\Django Projects\SichombaRobertTrail - Copy\myportfolio\myportfolio\urls.py

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

from portfolio import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- CORE PORTFOLIO URLS ---
    path('', views.portfolio_home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),

    # --- UNIFIED AUTHENTICATION ---
    path('signup/', views.portfolio_signup, name='portfolio_signup'),
    path('login/', views.portfolio_login, name='portfolio_login'),
    path('logout/', views.portfolio_logout, name='portfolio_logout'),

    # --- COURSE AUTHENTICATION ---
    path('courses/register/', views.course_register, name='course_register'),
    path('courses/login/', views.course_login, name='course_login'),

    # --- PASSWORD RESET (Django built-in) ---
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        form_class=views.CustomPasswordResetForm
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        form_class=views.CustomSetPasswordForm
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),

    # --- PORTFOLIO CONTENT ---
    path('projects/', views.projects_list, name='projects_list'),
    path('projects/<slug:slug>/', views.project_detail, name='project_detail'),

    path('testimonials/', views.testimonials_list, name='testimonials_list'),

    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),

    path('notes/', views.notes_list, name='notes_list'),
    path('notes/<slug:slug>/', views.note_detail, name='note_detail'),

    path('documents/', views.documents_list, name='documents_list'),
    path('documents/<slug:slug>/', views.document_detail, name='document_detail'),
    path('documents/<slug:slug>/download/', views.document_download, name='document_download'),

    path('books/', views.books_list, name='books_list'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),

    path('meetings/', views.meetings_list, name='meetings_list'),
    path('meetings/<slug:slug>/', views.meeting_detail, name='meeting_detail'),

    # --- COURSE MANAGEMENT ---
    # Main course pages
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path('courses/<str:school>/', views.CourseListView.as_view(), name='course_list_by_school'),
    path('course/<str:slug>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('course/<str:slug>/enroll/', views.enroll_course, name='enroll_course'),

    # Course learning
    path('course/<str:course_slug>/module/<int:module_id>/', views.course_module_detail, name='course_module_detail'),
    path('course/<str:course_slug>/lesson/<slug:lesson_slug>/', views.lesson_detail, name='lesson_detail'),

    # User dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/courses/', views.user_courses, name='user_courses'),
    path('dashboard/progress/', views.user_progress, name='user_progress'),
    path('dashboard/certificates/', views.user_certificates, name='user_certificates'),

    # User profile
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/update/', views.update_profile, name='profile_update'),

    # Assignments
    path('assignments/<str:assignment_id>/', views.assignment_detail, name='assignment_detail'),
    path('assignments/<str:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),
    path('submissions/<int:submission_id>/', views.submission_detail, name='submission_detail'),

    # Resources
    path('resources/', views.ResourceListView.as_view(), name='resource_list'),
    path('resources/<str:resource_id>/download/', views.download_resource, name='download_resource'),

    # Email verification
    path('verify-email/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),

    # Parent connections
path('parent/dashboard/', views.parent_dashboard, name='parent_dashboard'),
path('parent/connect/', views.parent_connect, name='parent_connect'),
path('parent/student/<int:student_id>/', views.parent_student_detail, name='parent_student_detail'),
path('parent/cancel/<int:connection_id>/', views.parent_cancel_connection, name='parent_cancel_connection'),
#path('parent/notifications/', views.parent_notifications, name='parent_notifications'),  # optional
    # Instructor Course Management
path('instructor/dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
path('instructor/courses/', views.instructor_course_list, name='instructor_course_list'),
path('instructor/course/create/', views.instructor_course_create, name='instructor_course_create'),
path('instructor/course/<slug:slug>/edit/', views.instructor_course_edit, name='instructor_course_edit'),
path('instructor/course/<slug:slug>/modules/', views.instructor_manage_modules, name='instructor_manage_modules'),
path('instructor/module/<int:module_id>/lesson/create/', views.instructor_lesson_create, name='instructor_lesson_create'),
path('instructor/lesson/<slug:slug>/edit/', views.instructor_lesson_edit, name='instructor_lesson_edit'),
path('instructor/course/<slug:slug>/assignments/', views.instructor_assignment_list, name='instructor_assignment_list'),
path('instructor/assignment/create/', views.instructor_assignment_create, name='instructor_assignment_create'),
path('instructor/assignment/<str:assignment_id>/edit/', views.instructor_assignment_edit, name='instructor_assignment_edit'),
path('instructor/assignment/<str:assignment_id>/submissions/', views.instructor_submissions_list, name='instructor_submissions_list'),
path('instructor/submission/<int:submission_id>/grade/', views.instructor_grade_submission, name='instructor_grade_submission'),


    # API endpoints
    path('api/user-progress/', views.api_user_progress, name='api_user_progress'),
    path('api/course-stats/', views.api_course_stats, name='api_course_stats'),
]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Error handlers
handler404 = 'portfolio.views.custom_404'
handler500 = 'portfolio.views.custom_500'