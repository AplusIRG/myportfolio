# urls.py in your portfolio app
from django.urls import path
from . import views

urlpatterns = [
    # Initial Landing Page and Dashboard
    path('dashboard/', views.home, name='home'),
    path('about/', views.about, name='about'),

    # User Authentication Paths
    path('signup/', views.user_signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Portfolio Content - Publicly Accessible
    path('projects/', views.projects_list, name='projects_list'),
    path('projects/<slug:slug>/', views.project_detail, name='project_detail'),
    path('testimonials/', views.testimonials_list, name='testimonials_list'),

    # Protected Content - Requires Login
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('notes/', views.notes_list, name='notes_list'),
    path('notes/<slug:slug>/', views.note_detail, name='note_detail'),
    path('notes/<int:pk>/', views.note_detail_by_id, name='note_detail_by_id'),
    
    path('documents/', views.documents_list, name='documents_list'),
    path('documents/<slug:slug>/', views.document_detail, name='document_detail'),
    
    path('books/', views.books_list, name='books_list'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    
    path('meetings/', views.meetings_list, name='meetings_list'),
    path('meetings/<slug:slug>/', views.meeting_detail, name='meeting_detail'),

    # Course System
    path('courses/', views.courses_list, name='courses_list'),
    path('courses/<slug:slug>/', views.course_detail, name='course_detail'),
    path('courses/<slug:slug>/enroll/', views.course_enroll, name='course_enroll'),
    path('courses/<slug:slug>/dashboard/', views.course_dashboard, name='course_dashboard'),
    path('courses/<slug:slug>/complete/<int:module_id>/', views.complete_module, name='complete_module'),
    path('courses/<slug:slug>/schedule/', views.course_schedule, name='course_schedule'),
    path('courses/<slug:slug>/faq/', views.course_faq, name='course_faq'),
    path('courses/<slug:slug>/team/', views.course_team, name='course_team'),
    path('my-courses/', views.my_courses, name='my_courses'),

    # Utility Pages
    path('contact/', views.contact, name='contact'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
]