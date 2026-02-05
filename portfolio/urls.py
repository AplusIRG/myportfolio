from django.urls import path
from . import views

urlpatterns = [
    # Initial Landing Page and Dashboard
    # The root path '' will now redirect to 'about' in the project-level urls.py
    # 'home' will serve as the dashboard for logged-in users.
    path('dashboard/', views.home, name='home'),
    path('about/', views.about, name='about'),

    # User Authentication Paths
    path('signup/', views.user_signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Portfolio Content - Publicly Accessible (or handled by view logic)
    path('projects/', views.projects_list, name='projects_list'),
    path('projects/<slug:slug>/', views.project_detail, name='project_detail'),
    path('testimonials/', views.testimonials_list, name='testimonials_list'),

    # Protected Content - Requires Login
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('notes/', views.notes_list, name='notes_list'),
    path('notes/<slug:slug>/', views.note_detail, name='note_detail'),
    path('documents/', views.documents_list, name='documents_list'),
    path('documents/<slug:slug>/', views.document_detail, name='document_detail'),
    # If you implement a direct download link, uncomment this:
    # path('documents/<slug:slug>/download/', views.download_document, name='download_document'),

    path('books/', views.books_list, name='books_list'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'), # Using PK, can change to slug if preferred

    path('meetings/', views.meetings_list, name='meetings_list'),
    path('meetings/<slug:slug>/', views.meeting_detail, name='meeting_detail'),

    # Utility Pages (Contact, Terms, Privacy)
    path('contact/', views.contact_view, name='contact'),
   

    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
]