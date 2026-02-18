# D:\Django Projects\SichombaRobertTrail - Copy\myportfolio\portfolio\views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.http import JsonResponse, HttpResponse, Http404, FileResponse
from django.views.generic import TemplateView, ListView, DetailView
from django.utils.decorators import method_decorator
from django.db.models import Q, Count, Avg, Sum
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.utils import timezone
import datetime
import json

import os

# Import all models
from .models import (
    CustomUser, Skill, Project, Testimonial, BlogPost,
    Note, Document, Book, Meeting, ContactMessage,
    Course, Enrollment, UserProgress, CourseModule, Lesson,
    Assignment, Submission, EmailVerification, ParentConnection,
    Certificate, CourseReview
)

# Import all forms
from .forms import (
    SignUpForm, CustomAuthenticationForm, ContactForm,
    CourseRegistrationForm, CourseLoginForm, CourseEnrollmentForm,
    AssignmentSubmissionForm, ParentConnectionForm, EmailVerificationForm,
    UserProfileUpdateForm, CourseInquiryForm, CustomPasswordResetForm,
    CustomSetPasswordForm
)

# ============================================================================
# CORE PORTFOLIO VIEWS
# ============================================================================

def portfolio_home(request):
    """Home page – redirects to about if not authenticated, shows dashboard if authenticated."""
    if not request.user.is_authenticated:
        return redirect('about')
    
    user = request.user
    
    if user.role == 'visitor':
        # Portfolio visitor dashboard
        featured_projects = Project.objects.filter(is_featured=True, status='completed')[:3]
        latest_blog_posts = BlogPost.objects.filter(
            is_published=True,
            access_level__in=['public', 'registered']
        ).order_by('-created_at')[:3]
        testimonials = Testimonial.objects.filter(is_featured=True)[:3]
        featured_courses = Course.objects.filter(is_featured=True, is_active=True)[:3]
        
        context = {
            'featured_projects': featured_projects,
            'latest_blog_posts': latest_blog_posts,
            'testimonials': testimonials,
            'featured_courses': featured_courses,
            'page_title': "Welcome to Your Portfolio Dashboard"
        }
        return render(request, 'home.html', context)
    
    elif user.role in ['student', 'instructor', 'parent']:
        return redirect('dashboard')
    else:
        # Admin or other roles
        return render(request, 'admin_dashboard.html')


def about(request):
    """Public about page."""
    skills = Skill.objects.all().order_by('-proficiency')
    testimonials = Testimonial.objects.filter(is_featured=True)[:3]
    
    context = {
        'skills': skills,
        'testimonials': testimonials,
        'page_title': 'About Me'
    }
    return render(request, 'about.html', context)


def portfolio_signup(request):
    """Portfolio visitor signup."""
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect('home')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome.')
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').capitalize()}: {error}")
    else:
        form = SignUpForm()
    
    context = {'form': form, 'page_title': 'Sign Up'}
    return render(request, 'registration/signup.html', context)


def portfolio_login(request):
    """Portfolio visitor login."""
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_display_name()}!")
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid email or password.")
    else:
        form = CustomAuthenticationForm()
    
    context = {'form': form, 'page_title': 'Login'}
    return render(request, 'registration/login.html', context)


def portfolio_logout(request):
    """Logout for portfolio users."""
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('about')


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            try:
                # Save the message to database (if your form has a save method)
                contact_message = form.save(user=request.user if request.user.is_authenticated else None)
            except Exception as e:
                logger.error(f"Error saving contact message: {e}")
                messages.error(request, 'There was an error saving your message.')
                return redirect('contact')
            
            # Try to send email, but don't crash if it fails
            try:
                send_mail(
                    f"New Contact: {form.cleaned_data['subject']}",
                    f"From: {form.cleaned_data['name']} ({form.cleaned_data['email']})\n\n{form.cleaned_data['message']}",
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.CONTACT_EMAIL],
                    fail_silently=True,   # Don't raise exception on failure
                )
                messages.success(request, 'Your message has been sent!')
            except Exception as e:
                logger.error(f"Error sending email: {e}")
                messages.warning(request, 'Your message was saved, but email notification could not be sent.')
            
            return redirect('contact')
    else:
        form = ContactForm()
    
    context = {'form': form, 'page_title': 'Contact'}
    return render(request, 'contact.html', context)

def terms(request):
    """Terms and conditions."""
    return render(request, 'terms.html', {'page_title': 'Terms of Service'})


def privacy(request):
    """Privacy policy."""
    return render(request, 'privacy.html', {'page_title': 'Privacy Policy'})


# ============================================================================
# PORTFOLIO CONTENT VIEWS
# ============================================================================

def projects_list(request):
    """List all projects."""
    projects = Project.objects.all().order_by('-created_at')
    skills = Skill.objects.all()
    completed_count = Project.objects.filter(status='completed').count()
    featured_count = Project.objects.filter(is_featured=True).count()
    
    context = {
        'projects': projects,
        'skills': skills,
        'completed_count': completed_count,
        'featured_count': featured_count,
        'page_title': 'My Projects'
    }
    return render(request, 'projects/projects_list.html', context)


def project_detail(request, slug):
    """Project detail view."""
    project = get_object_or_404(Project, slug=slug)
    
    # Simple access check (private projects only for staff)
    if project.status == 'private' and not request.user.is_staff:
        raise Http404("Project not found")
    
    # Related projects (same skills)
    related_projects = Project.objects.filter(
        skills_used__in=project.skills_used.all()
    ).exclude(id=project.id).distinct()[:3]
    
    context = {
        'project': project,
        'related_projects': related_projects,
        'page_title': project.title
    }
    return render(request, 'projects/project_detail.html', context)


import logging
logger = logging.getLogger(__name__)

def testimonials_list(request):
    try:
        testimonials = Testimonial.objects.all().order_by('-created_at')
        featured_testimonials = testimonials.filter(is_featured=True)
        featured_count = featured_testimonials.count()
        client_count = testimonials.filter(role__icontains='CEO') | testimonials.filter(role__icontains='Manager')
        student_count = testimonials.filter(role__icontains='Student')
        context = {
            'testimonials': testimonials,
            'featured_testimonials': featured_testimonials,
            'featured_count': featured_count,
            'client_count': client_count.count(),
            'student_count': student_count.count(),
            'page_title': 'Testimonials'
        }
        return render(request, 'testimonials/testimonials_list.html', context)
    except Exception as e:
        logger.exception("Error in testimonials_list")
        # Return a simple page with a friendly message instead of crashing
        return render(request, 'testimonials/testimonials_list.html', {'testimonials': []})

@login_required
def blog_list(request):
    """List blog posts with access control."""
    if request.user.is_superuser or request.user.is_staff:
        blog_posts = BlogPost.objects.filter(is_published=True).order_by('-created_at')
    else:
        blog_posts = BlogPost.objects.filter(
            is_published=True,
            access_level__in=['public', 'registered']
        ).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(blog_posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    category_choices = BlogPost.CATEGORY_CHOICES
    current_category = request.GET.get('category')
    
    # Category counts
    category_counts = {}
    for value, _ in category_choices:
        count = BlogPost.objects.filter(category=value, is_published=True).count()
        category_counts[value] = count
    
    recent_posts = BlogPost.objects.filter(is_published=True).order_by('-created_at')[:5]
    
    context = {
        'blog_posts': page_obj,
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages > 1,
        'category_choices': category_choices,
        'current_category': current_category,
        'category_counts': category_counts,
        'recent_posts': recent_posts,
        'total_posts': blog_posts.count(),
        'page_title': 'Blog'
    }
    return render(request, 'blog/blog_list.html', context)


@login_required
def blog_detail(request, slug):
    """Blog post detail with access control."""
    blog_post = get_object_or_404(BlogPost, slug=slug)
    
    # Access control
    if not blog_post.is_published:
        raise Http404("Blog post not found.")
    
    if blog_post.access_level == 'private':
        if not (request.user.is_staff or request.user.is_superuser):
            raise Http404("Blog post not found.")
    elif blog_post.access_level == 'registered':
        if not request.user.is_authenticated:
            messages.warning(request, "Please login to view this content.")
            return redirect('portfolio_login')
    elif blog_post.access_level == 'course_students':
        if not blog_post.related_courses.exists():
            # No specific course, treat as registered
            if not request.user.is_authenticated:
                messages.warning(request, "Please login to view this content.")
                return redirect('portfolio_login')
        else:
            # Check if user is enrolled in any of the related courses
            enrolled = Enrollment.objects.filter(
                user=request.user,
                course__in=blog_post.related_courses.all()
            ).exists()
            if not enrolled and not request.user.is_staff:
                messages.error(request, "You must be enrolled in the related course to view this content.")
                return redirect('course_list')
    
    # Increment view count
    blog_post.views += 1
    blog_post.save(update_fields=['views'])
    
    # Related posts
    related_posts = BlogPost.objects.filter(
        category=blog_post.category,
        is_published=True
    ).exclude(id=blog_post.id)[:3]
    
    # Popular posts
    popular_posts = BlogPost.objects.filter(is_published=True).order_by('-views')[:5]
    
    context = {
        'blog_post': blog_post,
        'related_posts': related_posts,
        'popular_posts': popular_posts,
        'page_title': blog_post.title
    }
    return render(request, 'blog/blog_detail.html', context)


@login_required
def notes_list(request):
    """List notes with access control."""
    if request.user.is_superuser or request.user.is_staff:
        notes = Note.objects.filter(is_published=True).order_by('-created_at')
    else:
        notes = Note.objects.filter(
            is_published=True,
            access_level__in=['public', 'registered']
        ).order_by('-created_at')
        
        # Add user's own private notes
        private_notes = Note.objects.filter(
            author=request.user,
            is_published=True,
            access_level='private'
        )
        notes = notes | private_notes
    
    # Pagination
    paginator = Paginator(notes, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    recent_notes = notes[:5]
    
    context = {
        'notes': page_obj,
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages > 1,
        'recent_notes': recent_notes,
        'total_notes': notes.count(),
        'public_notes': Note.objects.filter(is_published=True, access_level='public').count(),
        'my_notes': Note.objects.filter(author=request.user).count(),
        'page_title': 'Notes'
    }
    return render(request, 'notes/notes_list.html', context)


@login_required
def note_detail(request, slug):
    """Note detail with access control."""
    note = get_object_or_404(Note, slug=slug)
    
    if not note.is_published:
        raise Http404("Note not found.")
    
    # Access control
    if note.access_level == 'private':
        if note.author != request.user and not request.user.is_staff:
            raise Http404("Note not found.")
    elif note.access_level == 'registered':
        if not request.user.is_authenticated:
            messages.warning(request, "Please login to view this content.")
            return redirect('portfolio_login')
    elif note.access_level == 'course_students':
        if note.course:
            enrolled = Enrollment.objects.filter(
                user=request.user,
                course=note.course
            ).exists()
            if not enrolled and not request.user.is_staff:
                messages.error(request, "You must be enrolled in the course to view this note.")
                return redirect('course_detail', slug=note.course.slug)
    
    # Related notes
    related_notes = Note.objects.filter(
        author=note.author,
        is_published=True
    ).exclude(id=note.id)[:5]
    
    context = {
        'note': note,
        'related_notes': related_notes,
        'page_title': note.title
    }
    return render(request, 'notes/note_detail.html', context)


@login_required
def documents_list(request):
    """List documents with access control."""
    base_qs = Document.objects.filter(is_published=True)

    if request.user.is_superuser or request.user.is_staff:
        documents = base_qs.order_by('-uploaded_at')
    else:
        # Public and registered
        documents = base_qs.filter(
            access_level__in=['public', 'registered']
        ).order_by('-uploaded_at')

        # Course student accessible documents
        enrolled_courses = Enrollment.objects.filter(user=request.user).values_list('course', flat=True)
        course_docs = base_qs.filter(
            access_level='course_students',
            course__in=enrolled_courses
        )
        documents = documents | course_docs

        # User's own private documents
        private_docs = base_qs.filter(
            owner=request.user,
            access_level='private'
        )
        documents = documents | private_docs

    documents = documents.distinct()

    # Pagination
    paginator = Paginator(documents, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    top_downloads = Document.objects.filter(is_published=True).order_by('-download_count')[:5]

    # ✅ FIX: Use Sum() directly – no 'models.' prefix
    total_downloads = Document.objects.aggregate(total=Sum('download_count'))['total'] or 0

    context = {
        'documents': page_obj,
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages > 1,
        'document_types': Document.DOCUMENT_TYPE_CHOICES,
        'top_downloads': top_downloads,
        'total_documents': Document.objects.filter(is_published=True).count(),
        'total_downloads': total_downloads,
        'public_documents': Document.objects.filter(is_published=True, access_level='public').count(),
        'my_documents': Document.objects.filter(owner=request.user).count() if request.user.is_authenticated else 0,
        'page_title': 'Documents'
    }
    return render(request, 'documents/documents_list.html', context)


@login_required
def document_detail(request, slug):
    """Document detail with inline preview and download."""
    document = get_object_or_404(Document, slug=slug)

    if not document.is_published:
        raise Http404("Document not found.")

    # Determine preview type based on file extension
    file_extension = os.path.splitext(document.file.name)[1].lower()
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.bmp']
    text_extensions = ['.txt', '.csv', '.md', '.json', '.xml', '.html', '.css', '.js', '.py', '.java', '.c', '.cpp', '.h', '.rb', '.php']

    if file_extension == '.pdf':
        preview_type = 'pdf'
    elif file_extension in image_extensions:
        preview_type = 'image'
    elif file_extension in text_extensions:
        preview_type = 'text'
    else:
        preview_type = 'download'   # fallback – only download available

    # Access control (same as before)
    can_download = False
    if document.access_level == 'public':
        can_download = True
    elif document.access_level == 'registered' and request.user.is_authenticated:
        can_download = True
    elif document.access_level == 'course_students':
        if document.course:
            enrolled = Enrollment.objects.filter(
                user=request.user,
                course=document.course
            ).exists()
            if enrolled or request.user.is_staff:
                can_download = True
        elif request.user.is_authenticated:
            can_download = True
    elif document.access_level == 'private' and (document.owner == request.user or request.user.is_staff):
        can_download = True

    # Related documents
    related_documents = Document.objects.filter(
        is_published=True
    ).filter(
        Q(course=document.course) | Q(owner=document.owner)
    ).exclude(id=document.id)[:5]

    context = {
        'document': document,
        'can_download': can_download,
        'related_documents': related_documents,
        'preview_type': preview_type,
        'page_title': document.title
    }
    return render(request, 'documents/document_detail.html', context)
@login_required
def document_download(request, slug):
    """Serve document file with access control."""
    document = get_object_or_404(Document, slug=slug)
    
    # Access control (reuse logic)
    can_download = False
    if document.access_level == 'public':
        can_download = True
    elif document.access_level == 'registered' and request.user.is_authenticated:
        can_download = True
    elif document.access_level == 'course_students':
        if document.course:
            enrolled = Enrollment.objects.filter(
                user=request.user,
                course=document.course
            ).exists()
            if enrolled or request.user.is_staff:
                can_download = True
        elif request.user.is_authenticated:
            can_download = True
    elif document.access_level == 'private' and (document.owner == request.user or request.user.is_staff):
        can_download = True
    
    if not can_download:
        messages.error(request, "You do not have permission to download this document.")
        return redirect('document_detail', slug=slug)
    
    # Increment download count
    document.download_count += 1
    document.save(update_fields=['download_count'])
    
    response = FileResponse(
        document.file.open(),
        as_attachment=True,
        filename=document.file.name.split('/')[-1]
    )
    return response


@login_required
def books_list(request):
    """List books."""
    books = Book.objects.filter(access_level__in=['public', 'registered']).order_by('-created_at')
    
    context = {
        'books': books,
        'page_title': 'Recommended Books'
    }
    return render(request, 'books/books_list.html', context)


@login_required
def book_detail(request, pk):
    """Book detail."""
    book = get_object_or_404(Book, pk=pk)
    
    if book.access_level == 'registered' and not request.user.is_authenticated:
        messages.warning(request, "Please login to view details for this book.")
        return redirect('portfolio_login')
    
    context = {
        'book': book,
        'page_title': book.title
    }
    return render(request, 'books/book_detail.html', context)


@login_required
def meetings_list(request):
    """List available meetings."""
    today = datetime.date.today()
    now = datetime.datetime.now().time()
    
    meetings = Meeting.objects.filter(
        is_active=True,
        date__gte=today
    ).order_by('date', 'start_time')
    
    # Filter out past times for today
    meetings = [m for m in meetings if m.date > today or (m.date == today and m.start_time > now)]
    
    context = {
        'meetings': meetings,
        'page_title': 'Book a Meeting'
    }
    return render(request, 'meetings/meetings_list.html', context)


@login_required
def meeting_detail(request, slug):
    """Meeting detail and booking."""
    meeting = get_object_or_404(Meeting, slug=slug, is_active=True)
    
    if meeting.date < datetime.date.today() or (meeting.date == datetime.date.today() and meeting.start_time < datetime.datetime.now().time()):
        messages.error(request, "This meeting slot has already passed.")
        return redirect('meetings_list')
    
    if request.method == 'POST':
        if request.user in meeting.attendees.all():
            messages.info(request, "You are already registered for this meeting.")
        elif meeting.max_attendees and meeting.attendees.count() >= meeting.max_attendees:
            messages.error(request, "This meeting is full. Please choose another slot.")
        else:
            meeting.attendees.add(request.user)
            messages.success(request, f"You have successfully booked your spot for '{meeting.title}'!")
        return redirect('meeting_detail', slug=slug)
    
    is_attendee = request.user in meeting.attendees.all()
    
    context = {
        'meeting': meeting,
        'is_attendee': is_attendee,
        'current_attendees_count': meeting.attendees.count(),
        'page_title': meeting.title
    }
    return render(request, 'portfolio/meetings/detail.html', context)


# ============================================================================
# COURSE MANAGEMENT VIEWS
# ============================================================================

def course_register(request):
    """Course user registration."""
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CourseRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create verification code
            import random
            code = ''.join(random.choices('0123456789', k=6))
            EmailVerification.objects.create(
                user=user,
                code=code,
                verification_type='email_verification'
            )
            
            # In production, send email here
            messages.success(request, 'Account created! Please check your email for verification.')
            return redirect('course_login')
    else:
        form = CourseRegistrationForm()
    
    context = {'form': form, 'page_title': 'Course Registration'}
    return render(request, 'courses/auth/register.html', context)


def course_login(request):
    """Course login."""
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CourseLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.role != 'visitor' and not user.email_verified:
                messages.warning(request, 'Please verify your email first.')
                return redirect('verify_email')
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_display_name()}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid email or password.")
    else:
        form = CourseLoginForm()
    
    context = {'form': form, 'page_title': 'Course Login'}
    return render(request, 'courses/auth/login.html', context)


class CourseListView(ListView):
    """List all courses."""
    model = Course
    template_name = 'courses/list.html'
    context_object_name = 'courses'
    paginate_by = 12
    
    def get_queryset(self):
        school = self.kwargs.get('school')
        queryset = Course.objects.filter(is_active=True, is_open_for_enrollment=True)
        
        if school:
            queryset = queryset.filter(school=school)
        
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(course_code__icontains=search_query)
            )
        
        difficulty = self.request.GET.get('difficulty', '')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        level = self.request.GET.get('level', '')
        if level:
            queryset = queryset.filter(level=level)
        
        return queryset.order_by('course_code')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        school = self.kwargs.get('school')
        
        if school:
            context['school'] = dict(CustomUser.SCHOOL_CHOICES).get(school)
            context['school_key'] = school
        
        context['difficulty_choices'] = Course.DIFFICULTY_CHOICES
        context['level_choices'] = CustomUser.COURSE_LEVEL_CHOICES
        context['total_courses'] = Course.objects.filter(is_active=True).count()
        
        return context


class CourseDetailView(DetailView):
    """Course detail view."""
    model = Course
    template_name = 'courses/detail.html'
    context_object_name = 'course'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        
        if self.request.user.is_authenticated:
            context['is_enrolled'] = Enrollment.objects.filter(
                user=self.request.user, 
                course=course
            ).exists()
        
        context['modules'] = CourseModule.objects.filter(course=course, is_published=True).order_by('order')
        context['reviews'] = CourseReview.objects.filter(
            course=course, 
            is_approved=True
        ).order_by('-created_at')[:5]
        
        avg_rating = CourseReview.objects.filter(
            course=course, 
            is_approved=True
        ).aggregate(Avg('rating'))['rating__avg'] or 0
        context['average_rating'] = round(avg_rating, 1)
        
        # Using the new related_name 'projects_as_examples'
        context['related_projects'] = course.example_projects.all()[:3]
        context['related_skills'] = course.skills_taught.all()
        context['related_blog_posts'] = course.blog_posts.filter(is_published=True)[:3]
        
        return context


@login_required
def dashboard(request):
    """User dashboard."""
    user = request.user
    
    enrollments = Enrollment.objects.filter(user=user, status='active')
    courses = [enrollment.course for enrollment in enrollments]
    
    course_progress = []
    for course in courses:
        try:
            progress = UserProgress.objects.get(user=user, course=course)
            course_progress.append({
                'course': course,
                'progress': progress,
                'percentage': progress.calculate_progress()
            })
        except UserProgress.DoesNotExist:
            # Create default progress if not exists
            progress = UserProgress.objects.create(
                user=user,
                course=course,
                total_chapters=CourseModule.objects.filter(course=course, is_published=True).count()
            )
            course_progress.append({
                'course': course,
                'progress': progress,
                'percentage': 0
            })
    
    # Portfolio data for visitors or all users
    if user.role == 'visitor' or user.role == 'admin':
        featured_projects = Project.objects.filter(is_featured=True)[:3]
        latest_blog = BlogPost.objects.filter(is_published=True).order_by('-created_at')[:3]
    else:
        featured_projects = []
        latest_blog = []
    
    upcoming_assignments = Assignment.objects.filter(
        course__in=courses,
        due_date__gt=timezone.now()
    ).order_by('due_date')[:5]
    
    context = {
        'user': user,
        'course_progress': course_progress,
        'enrollments': enrollments,
        'featured_projects': featured_projects,
        'latest_blog': latest_blog,
        'upcoming_assignments': upcoming_assignments,
        'page_title': 'Dashboard'
    }
    
    return render(request, 'courses/dashboard.html', context)


@login_required
def user_courses(request):
    """List user's enrolled courses with progress."""
    enrollments = Enrollment.objects.filter(
        user=request.user, 
        status='active'
    ).select_related('course')

    # Attach progress to each enrollment (avoids template filtering)
    for enrollment in enrollments:
        try:
            enrollment.progress = UserProgress.objects.get(
                user=request.user, 
                course=enrollment.course
            )
        except UserProgress.DoesNotExist:
            enrollment.progress = None

    return render(request, 'courses/user_courses.html', {
        'enrollments': enrollments,
        'page_title': 'My Courses'
    })


@login_required
def user_progress(request):
    """Show user's progress across all courses."""
    progress_records = UserProgress.objects.filter(user=request.user)
    return render(request, 'courses/user_progress.html', {
        'progress_records': progress_records,
        'page_title': 'My Progress'
    })


@login_required
def user_certificates(request):
    """Show user's certificates."""
    certificates = Certificate.objects.filter(user=request.user)
    return render(request, 'courses/user_certificates.html', {
        'certificates': certificates,
        'page_title': 'My Certificates'
    })


@login_required
def user_profile(request):
    """User profile page."""
    user = request.user
    enrollments = Enrollment.objects.filter(user=user)
    certificates = Certificate.objects.filter(user=user)
    
    context = {
        'user': user,
        'enrollments': enrollments,
        'certificates': certificates,
        'page_title': 'My Profile'
    }
    return render(request, 'courses/profile/view.html', context)


@login_required
def update_profile(request):
    """Update user profile."""
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('user_profile')
    else:
        form = UserProfileUpdateForm(instance=request.user)
    
    context = {'form': form, 'page_title': 'Update Profile'}
    return render(request, 'courses/profile/update.html', context)


@login_required
def enroll_course(request, slug):
    """Enroll user in a course."""
    course = get_object_or_404(Course, slug=slug, is_active=True, is_open_for_enrollment=True)

    if Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.info(request, f"You are already enrolled in {course.title}")
        return redirect('course_detail', slug=slug)

    if not course.is_free and course.price > 0:
        messages.info(request, f"Payment required for {course.title}")
        return redirect('course_detail', slug=slug)

    # Create enrollment
    enrollment = Enrollment.objects.create(
        user=request.user,
        course=course,
        status='active'
    )

    # Get total published chapters
    total_chapters = CourseModule.objects.filter(course=course, is_published=True).count()

    # Create progress record
    UserProgress.objects.create(
        user=request.user,
        course=course,
        total_chapters=total_chapters,
        current_chapter=1  # start at module 1
    )

    messages.success(request, f"Successfully enrolled in {course.title}!")

    # ✅ Redirect to first module if exists, else to course detail
    first_module = CourseModule.objects.filter(course=course, is_published=True).order_by('order').first()
    if first_module:
        return redirect('course_module_detail', course_slug=slug, module_id=first_module.id)
    else:
        messages.info(request, "This course has no content yet. Please check back later.")
        return redirect('course_detail', slug=slug)

@login_required
def course_module_detail(request, course_slug, module_id):
    """Course module detail view."""
    course = get_object_or_404(Course, slug=course_slug)

    # Check enrollment
    if not Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.error(request, "You must be enrolled in this course to view its content.")
        return redirect('course_detail', slug=course_slug)

    # Try to get the requested module
    try:
        module = CourseModule.objects.get(course=course, id=module_id, is_published=True)
    except CourseModule.DoesNotExist:
        messages.warning(request, "The requested module does not exist or is not published.")
        return redirect('course_detail', slug=course_slug)

    # Get lessons for this module
    lessons = Lesson.objects.filter(module=module, is_published=True).order_by('order')

    # Get or create progress
    progress, created = UserProgress.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={
            'current_chapter': module_id,
            'total_chapters': CourseModule.objects.filter(course=course, is_published=True).count()
        }
    )

    if not created and progress.current_chapter != module_id:
        progress.current_chapter = module_id
        progress.save()

    context = {
        'course': course,
        'module': module,
        'lessons': lessons,
        'progress': progress,
        'page_title': f"{module.title} - {course.title}"
    }
    return render(request, 'courses/module_detail.html', context)
@login_required
def lesson_detail(request, course_slug, lesson_slug):
    """Lesson detail view."""
    course = get_object_or_404(Course, slug=course_slug)
    lesson = get_object_or_404(Lesson, slug=lesson_slug, module__course=course)
    
    if not Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.error(request, "You must be enrolled in this course to view its content.")
        return redirect('course_detail', slug=course_slug)
    
    lessons = Lesson.objects.filter(module=lesson.module, is_published=True).order_by('order')
    lesson_index = list(lessons).index(lesson) if lesson in lessons else -1
    next_lesson = lessons[lesson_index + 1] if lesson_index + 1 < len(lessons) else None
    prev_lesson = lessons[lesson_index - 1] if lesson_index - 1 >= 0 else None
    
    if lesson.requires_completion:
        progress = UserProgress.objects.get(user=request.user, course=course)
        completed_lessons = progress.completed_lessons or []
        if lesson.id not in completed_lessons:
            completed_lessons.append(lesson.id)
            progress.completed_lessons = completed_lessons
            progress.save()
    
    context = {
        'course': course,
        'lesson': lesson,
        'next_lesson': next_lesson,
        'prev_lesson': prev_lesson,
        'attached_documents': lesson.attached_documents.filter(is_published=True),
        'page_title': lesson.title
    }
    return render(request, 'courses/lesson_detail.html', context)


@login_required
def assignment_detail(request, assignment_id):
    """Assignment detail view."""
    assignment = get_object_or_404(Assignment, assignment_id=assignment_id)
    
    if not Enrollment.objects.filter(user=request.user, course=assignment.course).exists():
        messages.error(request, "You must be enrolled in this course to view assignments.")
        return redirect('course_detail', slug=assignment.course.slug)
    
    existing_submission = Submission.objects.filter(
        user=request.user,
        assignment=assignment
    ).first()
    
    context = {
        'assignment': assignment,
        'existing_submission': existing_submission,
        'page_title': assignment.title
    }
    return render(request, 'courses/assignments/detail.html', context)


@login_required
def submit_assignment(request, assignment_id):
    """Submit assignment."""
    assignment = get_object_or_404(Assignment, assignment_id=assignment_id)
    
    if not Enrollment.objects.filter(user=request.user, course=assignment.course).exists():
        messages.error(request, "You must be enrolled in this course to submit assignments.")
        return redirect('course_detail', slug=assignment.course.slug)
    
    existing_submission = Submission.objects.filter(user=request.user, assignment=assignment).first()
    
    if request.method == 'POST':
        form = AssignmentSubmissionForm(request.POST, request.FILES, instance=existing_submission)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.user = request.user
            submission.assignment = assignment
            submission.save()
            
            progress, _ = UserProgress.objects.get_or_create(
                user=request.user,
                course=assignment.course
            )
            progress.assignments_submitted += 1
            progress.save()
            
            messages.success(request, "Assignment submitted successfully!")
            return redirect('assignment_detail', assignment_id=assignment_id)
    else:
        form = AssignmentSubmissionForm(instance=existing_submission)
    
    context = {
        'assignment': assignment,
        'form': form,
        'existing_submission': existing_submission,
        'page_title': f"Submit: {assignment.title}"
    }
    return render(request, 'courses/assignments/submit.html', context)


@login_required
def submission_detail(request, submission_id):
    """Submission detail view."""
    submission = get_object_or_404(Submission, id=submission_id)
    
    # Only the student who submitted, instructors of the course, and staff can view
    if not (submission.user == request.user or 
            request.user == submission.assignment.course.instructor or
            request.user.is_staff):
        raise Http404("Submission not found.")
    
    context = {
        'submission': submission,
        'page_title': f"Submission for {submission.assignment.title}"
    }
    return render(request, 'courses/assignments/submission_detail.html', context)


class ResourceListView(ListView):
    """List all resources (documents) for courses."""
    model = Document
    template_name = 'courses/resources/list.html'
    context_object_name = 'resources'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Document.objects.filter(is_published=True)
        
        # Filter by course if provided
        course_id = self.request.GET.get('course')
        if course_id:
            queryset = queryset.filter(course__course_id=course_id)
        
        # Filter by resource type if provided
        resource_type = self.request.GET.get('type')
        if resource_type:
            queryset = queryset.filter(document_type=resource_type)
        
        # Access control: only show documents the user can access
        user = self.request.user
        if not user.is_authenticated:
            queryset = queryset.filter(access_level='public')
        elif not (user.is_staff or user.is_superuser):
            # Registered users can see public, registered, and course_students for their courses
            enrolled_courses = Enrollment.objects.filter(user=user).values_list('course', flat=True)
            queryset = queryset.filter(
                Q(access_level='public') |
                Q(access_level='registered') |
                (Q(access_level='course_students') & Q(course__in=enrolled_courses)) |
                Q(owner=user)  # own private docs
            ).distinct()
        
        return queryset.order_by('-uploaded_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resource_categories'] = Document.DOCUMENT_TYPE_CHOICES
        context['courses'] = Course.objects.filter(is_active=True)
        return context


@login_required
def download_resource(request, resource_id):
    """Alias for document_download, for course resources."""
    # resource_id is the primary key of Document
    document = get_object_or_404(Document, id=resource_id)
    return document_download(request, document.slug)


@login_required
def verify_email(request):
    """Email verification view."""
    if request.method == 'POST':
        form = EmailVerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            verification = EmailVerification.objects.filter(
                user=request.user,
                code=code,
                is_used=False
            ).first()
            if verification and not verification.is_expired():
                verification.is_used = True
                verification.save()
                request.user.email_verified = True
                request.user.save()
                messages.success(request, 'Email verified successfully!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid or expired verification code.')
    else:
        form = EmailVerificationForm()
    
    context = {'form': form, 'page_title': 'Verify Email'}
    return render(request, 'courses/auth/verify_email.html', context)


@login_required
def resend_verification(request):
    """Resend verification email."""
    import random
    code = ''.join(random.choices('0123456789', k=6))
    EmailVerification.objects.create(
        user=request.user,
        code=code,
        verification_type='email_verification'
    )
    # In production: send email
    messages.info(request, 'Verification code sent to your email.')
    return redirect('verify_email')


@login_required
def parent_connect(request):
    """Parent connect to student."""
    if request.user.role != 'parent':
        messages.error(request, "Only parent accounts can connect to students.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ParentConnectionForm(request.POST, parent=request.user)
        if form.is_valid():
            connection = form.save()
            messages.success(request, "Connection request sent to student. They need to verify.")
            return redirect('parent_dashboard')
    else:
        form = ParentConnectionForm(parent=request.user)
    
    context = {'form': form, 'page_title': 'Connect to Student'}
    return render(request, 'courses/parent/connect.html', context)


@login_required
def parent_dashboard(request):
    """Parent dashboard."""
    if request.user.role != 'parent':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    
    connections = ParentConnection.objects.filter(parent=request.user, is_verified=True)
    students = [conn.student for conn in connections]
    
    pending_connections = ParentConnection.objects.filter(parent=request.user, is_verified=False)
    
    context = {
        'connections': connections,
        'students': students,
        'pending_connections': pending_connections,
        'page_title': 'Parent Dashboard'
    }
    return render(request, 'courses/parent/dashboard.html', context)


# ============================================================================
# API VIEWS
# ============================================================================

@login_required
def api_user_progress(request):
    """API endpoint for user progress."""
    user = request.user
    progress_data = UserProgress.objects.filter(user=user).values(
        'course__title', 'course__course_code', 'chapters_completed',
        'total_chapters', 'grade', 'time_spent', 'streak_days'
    )
    return JsonResponse({'success': True, 'progress': list(progress_data)})


@login_required
def api_course_stats(request):
    """API endpoint for course statistics."""
    user = request.user
    if user.role == 'instructor':
        courses = Course.objects.filter(instructor=user)
        stats = []
        for course in courses:
            enrollments = Enrollment.objects.filter(course=course).count()
            avg_grade = UserProgress.objects.filter(course=course).aggregate(Avg('grade'))['grade__avg'] or 0
            stats.append({
                'course': course.title,
                'enrollments': enrollments,
                'average_grade': round(avg_grade, 1),
                'revenue': 0  # Placeholder
            })
    else:
        stats = []
    return JsonResponse({'success': True, 'stats': stats})


# ============================================================================
# ERROR HANDLERS
# ============================================================================

def custom_404(request, exception):
    return render(request, 'errors/404.html', status=404)

def custom_500(request):
    return render(request, 'errors/500.html', status=500)












from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse

# ============================================================================
# INSTRUCTOR DASHBOARD & COURSE MANAGEMENT
# ============================================================================

@login_required
def instructor_dashboard(request):
    """Instructor dashboard with stats and quick links."""
    if request.user.role != 'instructor':
        messages.error(request, "Access denied. Instructor privileges required.")
        return redirect('dashboard')
    
    courses = Course.objects.filter(instructor=request.user)
    total_students = Enrollment.objects.filter(course__in=courses).count()
    total_assignments = Assignment.objects.filter(course__in=courses).count()
    pending_submissions = Submission.objects.filter(
        assignment__course__in=courses,
        is_graded=False
    ).count()
    
    context = {
        'courses': courses,
        'total_courses': courses.count(),
        'total_students': total_students,
        'total_assignments': total_assignments,
        'pending_submissions': pending_submissions,
        'recent_courses': courses.order_by('-created_at')[:5],
        'page_title': 'Instructor Dashboard'
    }
    return render(request, 'courses/instructor/dashboard.html', context)


@login_required
def instructor_course_list(request):
    """List all courses taught by the instructor."""
    if request.user.role != 'instructor':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    
    courses = Course.objects.filter(instructor=request.user).order_by('-created_at')
    return render(request, 'courses/instructor/course_list.html', {
        'courses': courses,
        'page_title': 'My Courses'
    })


@login_required
def instructor_course_create(request):
    """Create a new course."""
    if request.user.role != 'instructor':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        # Process form data
        title = request.POST.get('title')
        course_code = request.POST.get('course_code')
        description = request.POST.get('description')
        detailed_description = request.POST.get('detailed_description')
        school = request.POST.get('school')
        department = request.POST.get('department')
        credits = request.POST.get('credits', 3)
        level = request.POST.get('level')
        duration = request.POST.get('duration')
        difficulty = request.POST.get('difficulty')
        price = request.POST.get('price', 0)
        is_free = request.POST.get('is_free') == 'on'
        thumbnail = request.FILES.get('thumbnail')
        
        # Generate course_id (you may want a more robust method)
        import random
        course_id = f"{course_code}-{random.randint(1000, 9999)}"
        
        course = Course.objects.create(
            course_id=course_id,
            course_code=course_code,
            title=title,
            description=description,
            detailed_description=detailed_description,
            school=school,
            department=department,
            instructor=request.user,
            credits=credits,
            level=level,
            duration=duration,
            difficulty=difficulty,
            price=price,
            is_free=is_free,
            thumbnail=thumbnail
        )
        messages.success(request, f"Course '{title}' created successfully!")
        return redirect('instructor_course_edit', slug=course.slug)
    
    context = {
        'school_choices': CustomUser.SCHOOL_CHOICES,
        'level_choices': CustomUser.COURSE_LEVEL_CHOICES,
        'difficulty_choices': Course.DIFFICULTY_CHOICES,
        'page_title': 'Create New Course'
    }
    return render(request, 'courses/instructor/course_form.html', context)


@login_required
def instructor_course_edit(request, slug):
    """Edit an existing course."""
    if request.user.role != 'instructor':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    
    course = get_object_or_404(Course, slug=slug, instructor=request.user)
    
    if request.method == 'POST':
        course.title = request.POST.get('title')
        course.course_code = request.POST.get('course_code')
        course.description = request.POST.get('description')
        course.detailed_description = request.POST.get('detailed_description')
        course.school = request.POST.get('school')
        course.department = request.POST.get('department')
        course.credits = request.POST.get('credits', 3)
        course.level = request.POST.get('level')
        course.duration = request.POST.get('duration')
        course.difficulty = request.POST.get('difficulty')
        course.price = request.POST.get('price', 0)
        course.is_free = request.POST.get('is_free') == 'on'
        if request.FILES.get('thumbnail'):
            course.thumbnail = request.FILES.get('thumbnail')
        course.save()
        
        messages.success(request, "Course updated successfully!")
        return redirect('instructor_course_edit', slug=course.slug)
    
    context = {
        'course': course,
        'school_choices': CustomUser.SCHOOL_CHOICES,
        'level_choices': CustomUser.COURSE_LEVEL_CHOICES,
        'difficulty_choices': Course.DIFFICULTY_CHOICES,
        'page_title': f'Edit {course.title}'
    }
    return render(request, 'courses/instructor/course_form.html', context)


@login_required
def instructor_manage_modules(request, slug):
    """Manage modules and lessons for a course."""
    if request.user.role != 'instructor':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    
    course = get_object_or_404(Course, slug=slug, instructor=request.user)
    modules = CourseModule.objects.filter(course=course).order_by('order')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_module':
            title = request.POST.get('title')
            description = request.POST.get('description')
            order = modules.count() + 1
            CourseModule.objects.create(
                course=course,
                title=title,
                description=description,
                order=order
            )
            messages.success(request, "Module added successfully.")
        
        elif action == 'delete_module':
            module_id = request.POST.get('module_id')
            CourseModule.objects.filter(id=module_id, course=course).delete()
            # Reorder remaining modules
            for idx, mod in enumerate(CourseModule.objects.filter(course=course).order_by('order'), start=1):
                mod.order = idx
                mod.save()
            messages.success(request, "Module deleted.")
        
        return redirect('instructor_manage_modules', slug=slug)
    
    context = {
        'course': course,
        'modules': modules,
        'page_title': f'Manage {course.title}'
    }
    return render(request, 'courses/instructor/module_manage.html', context)


@login_required
def instructor_lesson_create(request, module_id):
    """Create a new lesson in a module."""
    module = get_object_or_404(CourseModule, id=module_id)
    if module.course.instructor != request.user:
        messages.error(request, "Access denied.")
        return redirect('instructor_dashboard')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        video_url = request.POST.get('video_url')
        duration_minutes = request.POST.get('duration_minutes', 0)
        order = module.lessons.count() + 1
        
        lesson = Lesson.objects.create(
            module=module,
            title=title,
            content=content,
            video_url=video_url,
            duration_minutes=duration_minutes,
            order=order,
            slug=slugify(f"{module.course.course_code}-{title}")
        )
        messages.success(request, "Lesson created successfully.")
        return redirect('instructor_manage_modules', slug=module.course.slug)
    
    context = {
        'module': module,
        'course': module.course,
        'page_title': f'Add Lesson to {module.title}'
    }
    return render(request, 'courses/instructor/lesson_form.html', context)


@login_required
def instructor_lesson_edit(request, slug):
    """Edit an existing lesson."""
    lesson = get_object_or_404(Lesson, slug=slug)
    if lesson.module.course.instructor != request.user:
        messages.error(request, "Access denied.")
        return redirect('instructor_dashboard')
    
    if request.method == 'POST':
        lesson.title = request.POST.get('title')
        lesson.content = request.POST.get('content')
        lesson.video_url = request.POST.get('video_url')
        lesson.duration_minutes = request.POST.get('duration_minutes', 0)
        lesson.save()
        messages.success(request, "Lesson updated successfully.")
        return redirect('instructor_manage_modules', slug=lesson.module.course.slug)
    
    context = {
        'lesson': lesson,
        'module': lesson.module,
        'course': lesson.module.course,
        'page_title': f'Edit {lesson.title}'
    }
    return render(request, 'courses/instructor/lesson_form.html', context)


# ============================================================================
# ASSIGNMENT MANAGEMENT
# ============================================================================

@login_required
def instructor_assignment_list(request, slug):
    """List all assignments for a course."""
    course = get_object_or_404(Course, slug=slug, instructor=request.user)
    assignments = Assignment.objects.filter(course=course).order_by('-due_date')
    
    context = {
        'course': course,
        'assignments': assignments,
        'page_title': f'Assignments - {course.title}'
    }
    return render(request, 'courses/instructor/assignment_list.html', context)


@login_required
def instructor_assignment_create(request):
    """Create a new assignment."""
    if request.user.role != 'instructor':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        course_id = request.POST.get('course')
        course = get_object_or_404(Course, id=course_id, instructor=request.user)
        
        title = request.POST.get('title')
        description = request.POST.get('description')
        due_date = request.POST.get('due_date')
        max_points = request.POST.get('max_points', 100)
        assignment_type = request.POST.get('assignment_type')
        allows_file_upload = request.POST.get('allows_file_upload') == 'on'
        max_file_size_mb = request.POST.get('max_file_size_mb', 10)
        
        # Generate assignment_id
        import uuid
        assignment_id = f"{course.course_code}-{uuid.uuid4().hex[:6].upper()}"
        
        assignment = Assignment.objects.create(
            assignment_id=assignment_id,
            course=course,
            title=title,
            description=description,
            due_date=due_date,
            max_points=max_points,
            assignment_type=assignment_type,
            created_by=request.user,
            allows_file_upload=allows_file_upload,
            max_file_size_mb=max_file_size_mb
        )
        messages.success(request, "Assignment created successfully.")
        return redirect('instructor_assignment_list', slug=course.slug)
    
    courses = Course.objects.filter(instructor=request.user)
    context = {
        'courses': courses,
        'assignment_types': Assignment.ASSIGNMENT_TYPES,
        'page_title': 'Create Assignment'
    }
    return render(request, 'courses/instructor/assignment_form.html', context)


@login_required
def instructor_assignment_edit(request, assignment_id):
    """Edit an existing assignment."""
    assignment = get_object_or_404(Assignment, assignment_id=assignment_id)
    if assignment.course.instructor != request.user:
        messages.error(request, "Access denied.")
        return redirect('instructor_dashboard')
    
    if request.method == 'POST':
        assignment.title = request.POST.get('title')
        assignment.description = request.POST.get('description')
        assignment.due_date = request.POST.get('due_date')
        assignment.max_points = request.POST.get('max_points', 100)
        assignment.assignment_type = request.POST.get('assignment_type')
        assignment.allows_file_upload = request.POST.get('allows_file_upload') == 'on'
        assignment.max_file_size_mb = request.POST.get('max_file_size_mb', 10)
        assignment.save()
        messages.success(request, "Assignment updated successfully.")
        return redirect('instructor_assignment_list', slug=assignment.course.slug)
    
    context = {
        'assignment': assignment,
        'course': assignment.course,
        'assignment_types': Assignment.ASSIGNMENT_TYPES,
        'page_title': f'Edit {assignment.title}'
    }
    return render(request, 'courses/instructor/assignment_form.html', context)


@login_required
def instructor_submissions_list(request, assignment_id):
    """List all submissions for an assignment."""
    assignment = get_object_or_404(Assignment, assignment_id=assignment_id)
    if assignment.course.instructor != request.user:
        messages.error(request, "Access denied.")
        return redirect('instructor_dashboard')
    
    submissions = Submission.objects.filter(assignment=assignment).order_by('-submitted_at')
    enrolled_students = Enrollment.objects.filter(course=assignment.course, status='active')
    total_students = enrolled_students.count()
    submitted_count = submissions.count()
    
    context = {
        'assignment': assignment,
        'course': assignment.course,
        'submissions': submissions,
        'total_students': total_students,
        'submitted_count': submitted_count,
        'page_title': f'Submissions - {assignment.title}'
    }
    return render(request, 'courses/instructor/submissions_list.html', context)


@login_required
def instructor_grade_submission(request, submission_id):
    """Grade a specific submission."""
    submission = get_object_or_404(Submission, id=submission_id)
    if submission.assignment.course.instructor != request.user:
        messages.error(request, "Access denied.")
        return redirect('instructor_dashboard')
    
    if request.method == 'POST':
        grade = request.POST.get('grade')
        feedback = request.POST.get('feedback')
        
        submission.grade = grade
        submission.feedback = feedback
        submission.is_graded = True
        submission.graded_at = timezone.now()
        submission.graded_by = request.user
        submission.save()
        
        messages.success(request, f"Submission graded: {grade}/{submission.assignment.max_points}")
        return redirect('instructor_submissions_list', assignment_id=submission.assignment.assignment_id)
    
    context = {
        'submission': submission,
        'assignment': submission.assignment,
        'student': submission.user,
        'page_title': f'Grade {submission.user.get_display_name()}'
    }
    return render(request, 'courses/instructor/grade_submission.html', context)










@login_required
def parent_student_detail(request, student_id):
    """Show detailed progress for a specific student (parent view)."""
    if request.user.role != 'parent':
        messages.error(request, "Access denied.")
        return redirect('dashboard')

    # Verify this parent is connected to the student
    student = get_object_or_404(CustomUser, id=student_id, role='student')
    connection = get_object_or_404(ParentConnection, parent=request.user, student=student, is_verified=True)

    enrollments = Enrollment.objects.filter(user=student).select_related('course')
    completed_courses = enrollments.filter(completed=True).count()

    # Attach progress to each enrollment
    for enrollment in enrollments:
        try:
            enrollment.progress = UserProgress.objects.get(user=student, course=enrollment.course)
        except UserProgress.DoesNotExist:
            enrollment.progress = None

    avg_grade = 0
    graded_submissions = Submission.objects.filter(user=student, is_graded=True)
    if graded_submissions.exists():
        avg_grade = graded_submissions.aggregate(Avg('grade'))['grade__avg'] or 0

    recent_submissions = Submission.objects.filter(user=student).order_by('-submitted_at')[:5]
    certificates = Certificate.objects.filter(user=student)

    context = {
        'student': student,
        'enrollments': enrollments,
        'completed_courses': completed_courses,
        'avg_grade': avg_grade,
        'recent_submissions': recent_submissions,
        'certificates': certificates,
        'page_title': f"{student.get_display_name()} - Progress"
    }
    return render(request, 'parent/student_detail.html', context)








@require_POST
@login_required
def parent_cancel_connection(request, connection_id):
    if request.user.role != 'parent':
        return JsonResponse({'error': 'Access denied'}, status=403)
    connection = get_object_or_404(ParentConnection, id=connection_id, parent=request.user, is_verified=False)
    connection.delete()
    messages.success(request, "Connection request cancelled.")
    return redirect('parent_dashboard')