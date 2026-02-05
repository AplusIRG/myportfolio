# D:\Django Projects\robert - Copy (3)\myportfolio\myportfolio\urls.py

from django.contrib import admin
from django.urls import path, include

# THIS IS CORRECT: Importing Django's built-in auth views as auth_views
from django.contrib.auth import views as auth_views 

# ASSUMING 'portfolio' IS YOUR APP NAME:
# Import all views from your 'portfolio' app's views.py file
from portfolio import views 


urlpatterns = [
    path('admin/', admin.site.urls),

    # --- Core Website URLs ---
    # The root URL (/) now goes to your `home` view, which redirects unauthenticated users to 'about'
    path('', views.home, name='home'), # Corrected: using `views.home` not `views.home_view`
    
    # Your public 'about' page
    path('about/', views.about, name='about'), # Corrected: using `views.about` not `views.about_view`
    
    # Contact page
    path('contact/', views.contact, name='contact'),
   
    # Legal/Policy pages
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),

    # --- User Authentication URLs ---
    # Using your custom function-based views for signup/login/logout
    path('signup/', views.user_signup, name='signup'), # Corrected: using `views.user_signup`
    path('login/', views.user_login, name='login'), # Corrected: using `views.user_login`
    path('logout/', views.user_logout, name='logout'), # Corrected: using `views.user_logout`
    
    # Django's built-in password reset URLs (ensure your templates for these exist)
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

    # --- Portfolio Content URLs ---
    path('projects/', views.projects_list, name='projects_list'),
    path('projects/<slug:slug>/', views.project_detail, name='project_detail'),

    path('testimonials/', views.testimonials_list, name='testimonials_list'), # Matches your view name

    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),

    path('notes/', views.notes_list, name='notes_list'),
    path('notes/<slug:slug>/', views.note_detail, name='note_detail'),

    path('documents/', views.documents_list, name='documents_list'),
    path('documents/<slug:slug>/', views.document_detail, name='document_detail'),
    # If you implement a download view:
    # path('documents/<slug:slug>/download/', views.download_document, name='download_document'),

    path('books/', views.books_list, name='books_list'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),

    path('meetings/', views.meetings_list, name='meetings_list'),
    
    path('meetings/<slug:slug>/', views.meeting_detail, name='meeting_detail'),
    
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy_view'),

    path('terms-of-service/', views.terms_of_service_view, name='terms_of_service_view'),

    
]

# FOR DEVELOPMENT ONLY: Serving static and media files
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)