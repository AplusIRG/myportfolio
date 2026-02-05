# D:\Django Projects\robert - Copy (3)\myportfolio\portfolio\views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate # Import for authentication
from django.contrib.auth.decorators import login_required # Decorator for protecting views
from django.conf import settings # To access settings like CONTACT_EMAIL

from django.http import Http404 # <--- ADD THIS IMPORT
import datetime # <--- ADD THIS IMPORT


# Import your models
from .models import (
    Project, Skill, Testimonial, BlogPost,
    Note, Document, Book, Meeting, ContactMessage,
    CustomUser # Import your CustomUser if you need to query it
)

# Import your forms
from .forms import SignUpForm, ContactForm # Assuming you'll create a ContactForm
from django.contrib.auth.forms import AuthenticationForm # Django's built-in login form

from django.core.mail import send_mail # For contact form email

# --- Core Website Views (Publicly Accessible) ---

def about(request):
    """
    Renders the 'About' page. This is the initial landing page.
    Includes skills for display.
    """
    # Fetch all skills, ordered by proficiency
    skills = Skill.objects.all()

    context = {
        'linkedin_url': 'https://www.linkedin.com/in/robert-sichomba',
        'pitch_deck_url': 'https://example.com/pitch-deck', # Replace with your actual URL
        'contact_url': reverse('contact'), # Use reverse for robust URL linking
        'skills': skills, # Pass actual Skill objects
    }
    return render(request, 'about.html', context)


def home(request):
    """
    Renders the 'Home' dashboard-like page for logged-in users,
    or redirects to 'about' if not authenticated.
    """
    if not request.user.is_authenticated:
        # If not logged in, redirect to the about page as per your plan
        return redirect('about')

    # Content for logged-in users
    # Filter for featured or public content that logged-in users can see
    featured_projects = Project.objects.filter(is_featured=True, status='completed')[:3]
    latest_blog_posts = BlogPost.objects.filter(
        is_published=True,
        access_level__in=['public', 'registered'] # Users can see public or registered content
    ).order_by('-created_at')[:3]
    
    # Show recently added notes/documents (e.g., last 3 notes/documents)
    latest_notes = Note.objects.filter(
        is_published=True,
        access_level__in=['public', 'registered'],
        author=request.user if request.user.is_authenticated else None # Only show user's notes if logged in
    ).order_by('-created_at')[:3]

    latest_documents = Document.objects.filter(
        is_published=True,
        access_level__in=['public', 'registered']
    ).order_by('-uploaded_at')[:3]

    # You might also feature testimonials or recommended books here
    testimonials = Testimonial.objects.filter(is_featured=True)[:3]
    
    context = {
        'featured_projects': featured_projects,
        'latest_blog_posts': latest_blog_posts,
        'latest_notes': latest_notes,
        'latest_documents': latest_documents,
        'testimonials': testimonials,
        'page_title': "Welcome to Your Dashboard!"
    }
    return render(request, 'home.html', context) # This will now be your dashboard for logged-in users


def contact(request):
    """
    Handles the contact form submission.
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message_content = form.cleaned_data['message']

            # Save to database
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message_content
            )

            # Send email (ensure settings.DEFAULT_FROM_EMAIL and settings.CONTACT_EMAIL are configured)
            try:
                send_mail(
                    f"New Contact Form Submission: {subject}",
                    f"Name: {name}\nEmail: {email}\n\nMessage:\n{message_content}",
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.CONTACT_EMAIL],
                    fail_silently=False,
                )
                messages.success(request, 'Your message has been sent successfully! I will get back to you soon.')
            except Exception as e:
                messages.error(request, f'There was an issue sending your message. Please try again later. Error: {e}')
            
            return redirect('contact') # Redirect to the same page to prevent resubmission
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactForm()
    
    context = {
        'page_title': 'Contact Me',
        'contact_email': 'sichombarobertbob@gmail.com', # Consider moving this to settings
        'phone_number': '+260974609823', # Consider moving this to settings
        'form': form
    }
    return render(request, 'contact.html', context)


def terms(request):
    """Renders the Terms and Conditions page."""
    return render(request, 'terms.html')

def privacy(request):
    """Renders the Privacy Policy page."""
    return render(request, 'privacy.html')


# --- User Authentication Views ---

def user_signup(request):
    """
    Handles user registration.
    Redirects authenticated users away from the signup page.
    """
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect('home') # Redirect to dashboard if already logged in

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'Account created successfully! Welcome.')
            return redirect('home') # Redirect to dashboard after signup
        else:
            # Display specific errors from the form
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').capitalize()}: {error}")
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SignUpForm()
    
    context = {
        'form': form,
        'page_title': 'Sign Up'
    }
    return render(request, 'registration/signup.html', context) # Use a specific template path for registration

def user_login(request):
    """
    Handles user login.
    Redirects authenticated users away from the login page.
    """
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect('home') # Redirect to dashboard if already logged in

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username') # This will be the email as per CustomUser
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username or user.email}!")
                # Redirect to 'next' URL if provided (e.g., after trying to access a protected page)
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('home') # Default redirect to dashboard
            else:
                messages.error(request, "Invalid email or password.")
        else:
            messages.error(request, "Invalid email or password.") # General error for invalid form
    else:
        form = AuthenticationForm()
    
    context = {
        'form': form,
        'page_title': 'Login'
    }
    return render(request, 'registration/login.html', context) # Use a specific template path for registration

@login_required # Requires user to be logged in
def user_logout(request):
    """
    Logs out the current user.
    """
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('about') # Redirect to the public about page after logout


# --- Portfolio Content Views (Protected as needed) ---

def projects_list(request):
    """
    Displays a list of all projects.
    """
    all_projects = Project.objects.all().order_by('-created_at')
    context = {
        'projects': all_projects,
        'page_title': 'My Projects'
    }
    return render(request, 'projects/projects_list.html', context)

def project_detail(request, slug):
    """
    Displays details of a single project.
    """
    project = get_object_or_404(Project, slug=slug)
    context = {
        'project': project,
        'page_title': project.title
    }
    return render(request, 'projects/project_detail.html', context)


def testimonials_list(request):
    """
    Displays a list of all testimonials.
    """
    all_testimonials = Testimonial.objects.all().order_by('-created_at')
    context = {
        'testimonials': all_testimonials,
        'page_title': 'Testimonials'
    }
    return render(request, 'testimonials/testimonials_list.html', context)


@login_required # Only registered users can access
def blog_list(request):
    """
    Displays a list of blog posts accessible to the current user.
    """
    # Filter blog posts based on access level
    if request.user.is_superuser or request.user.is_staff: # Admin/Staff can see all published
        blog_posts = BlogPost.objects.filter(is_published=True).order_by('-created_at')
    else: # Regular registered users can see public and registered content
        blog_posts = BlogPost.objects.filter(
            is_published=True,
            access_level__in=['public', 'registered']
        ).order_by('-created_at')

    context = {
        'blog_posts': blog_posts,
        'page_title': 'My Blog'
    }
    return render(request, 'blog/blog_list.html', context)

@login_required # Only registered users can access
def blog_detail(request, slug):
    """
    Displays details of a single blog post, with access control.
    """
    blog_post = get_object_or_404(BlogPost, slug=slug)

    # Access control logic
    if blog_post.access_level == 'public' and not blog_post.is_published:
        # Public content not published should not be shown
        raise Http404("Blog post not found or not published.")
    elif blog_post.access_level == 'registered' and not request.user.is_authenticated:
        messages.warning(request, "Please log in to view this content.")
        return redirect(reverse('user_login') + f'?next={request.path}')
    elif blog_post.access_level == 'private' and not (request.user.is_staff or request.user.is_superuser or blog_post.author == request.user):
        messages.error(request, "You do not have permission to view this private content.")
        return redirect('home') # Or a 403 Forbidden page

    context = {
        'blog_post': blog_post,
        'page_title': blog_post.title
    }
    return render(request, 'blog/blog_detail.html', context)


@login_required # Only registered users can access
def notes_list(request):
    """
    Displays a list of notes accessible to the current user.
    """
    if request.user.is_superuser or request.user.is_staff:
        notes = Note.objects.filter(is_published=True).order_by('-created_at')
    else:
        notes = Note.objects.filter(
            is_published=True,
            access_level__in=['public', 'registered']
        ).order_by('-created_at')

    context = {
        'notes': notes,
        'page_title': 'My Notes'
    }
    return render(request, 'notes/notes_list.html', context)

@login_required # Only registered users can access
def note_detail(request, slug):
    """
    Displays details of a single note, with access control.
    """
    note = get_object_or_404(Note, slug=slug)

    if note.access_level == 'public' and not note.is_published:
        raise Http404("Note not found or not published.")
    elif note.access_level == 'registered' and not request.user.is_authenticated:
        messages.warning(request, "Please log in to view this content.")
        return redirect(reverse('user_login') + f'?next={request.path}')
    elif note.access_level == 'private' and not (request.user.is_staff or request.user.is_superuser or note.author == request.user):
        messages.error(request, "You do not have permission to view this private note.")
        return redirect('home')

    context = {
        'note': note,
        'page_title': note.title
    }
    return render(request, 'notes/note_detail.html', context)


@login_required # Only registered users can access
def documents_list(request):
    """
    Displays a list of documents accessible to the current user.
    """
    if request.user.is_superuser or request.user.is_staff:
        documents = Document.objects.filter(is_published=True).order_by('-uploaded_at')
    else:
        documents = Document.objects.filter(
            is_published=True,
            access_level__in=['public', 'registered']
        ).order_by('-uploaded_at')

    context = {
        'documents': documents,
        'page_title': 'My Documents'
    }
    return render(request, 'documents/documents_list.html', context)

@login_required # Only registered users can access
def document_detail(request, slug):
    """
    Displays details of a single document, with access control.
    Allows download.
    """
    document = get_object_or_404(Document, slug=slug)

    if document.access_level == 'public' and not document.is_published:
        raise Http404("Document not found or not published.")
    elif document.access_level == 'registered' and not request.user.is_authenticated:
        messages.warning(request, "Please log in to access this document.")
        return redirect(reverse('user_login') + f'?next={request.path}')
    elif document.access_level == 'private' and not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "You do not have permission to access this private document.")
        return redirect('home')

    context = {
        'document': document,
        'page_title': document.title
    }
    return render(request, 'documents/document_detail.html', context)

# You might want a direct download view for documents
# from django.http import FileResponse
# @login_required
# def download_document(request, slug):
#     document = get_object_or_404(Document, slug=slug, is_published=True, access_level__in=['public', 'registered'])
#     # Add robust access check here, similar to detail view
#     if document.access_level == 'registered' and not request.user.is_authenticated:
#         messages.warning(request, "Please log in to download this document.")
#         return redirect(reverse('user_login') + f'?next={request.path}')
#     elif document.access_level == 'private' and not (request.user.is_staff or request.user.is_superuser):
#         messages.error(request, "You do not have permission to download this private document.")
#         return redirect('home')
#     
#     return FileResponse(document.file.open(), as_attachment=True, filename=document.file.name)


@login_required # Only registered users can access
def books_list(request):
    """
    Displays a list of books accessible to the current user.
    """
    if request.user.is_superuser or request.user.is_staff:
        books = Book.objects.all().order_by('-created_at')
    else:
        books = Book.objects.filter(access_level__in=['public', 'registered']).order_by('-created_at')

    context = {
        'books': books,
        'page_title': 'Recommended Books'
    }
    return render(request, 'books/books_list.html', context)

@login_required # Only registered users can access
def book_detail(request, pk):
    """
    Displays details of a single book, with comprehensive access control.
    """
    book = get_object_or_404(Book, pk=pk) # Fetches the book by primary key

    # --- Access Control Logic ---

    # 1. Handle Private Access: Only superusers/staff can see private books
    if book.access_level == 'private':
        if not request.user.is_authenticated or (not request.user.is_superuser and not request.user.is_staff):
            raise Http404("Book not found or you do not have permission to access this private content.")
            # Alternatively, you could redirect to a permission denied page
            # messages.error(request, "You do not have permission to view this private content.")
            # return redirect('home') # Or a custom permission denied URL

    # 2. Handle Registered Access: Requires authentication
    if book.access_level == 'registered':
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to view details for this book.")
            return redirect(reverse('login') + f'?next={request.path}') # Use 'login' URL name

    # Public access does not require any special checks, as it's the default/least restrictive.

    context = {
        'book': book,
        'page_title': book.title
    }
    return render(request, 'books/book_detail.html', context)

@login_required # Only registered users can access meeting details/booking
def meetings_list(request):
    """
    Displays a list of available meetings/lectures.
    """
    # Filter for active meetings that are in the future
    today = datetime.date.today()
    now = datetime.datetime.now().time()

    # Get meetings that are today or in the future
    available_meetings = Meeting.objects.filter(
        is_active=True,
        date__gte=today,
    ).order_by('date', 'start_time')

    # For today's meetings, filter out past times
    available_meetings = [
        m for m in available_meetings if m.date > today or (m.date == today and m.start_time > now)
    ]
    
    context = {
        'meetings': available_meetings,
        'page_title': 'Book a Meeting'
    }
    return render(request, 'meetings/meetings_list.html', context)


@login_required
def meeting_detail(request, slug):
    """
    Displays details of a single meeting and handles booking.
    """
    meeting = get_object_or_404(Meeting, slug=slug, is_active=True)

    # Check if the meeting is in the past
    if meeting.date < datetime.date.today() or (meeting.date == datetime.date.today() and meeting.start_time < datetime.datetime.now().time()):
        messages.error(request, "This meeting slot has already passed.")
        return redirect('meetings_list')

    # Handle booking (joining) a meeting
    if request.method == 'POST':
        # Check if user is already an attendee
        if request.user in meeting.attendees.all():
            messages.info(request, "You are already registered for this meeting.")
            return redirect('meeting_detail', slug=slug)

        # Check if maximum attendees limit is reached (if applicable)
        if meeting.max_attendees and meeting.attendees.count() >= meeting.max_attendees:
            messages.error(request, "This meeting is full. Please choose another slot.")
            return redirect('meetings_list')

        # Add user to attendees
        meeting.attendees.add(request.user)
        messages.success(request, f"You have successfully booked your spot for '{meeting.title}'!")
        # Optionally, send a confirmation email here
        return redirect('meeting_detail', slug=slug)
    
    # Check if the user is already an attendee for display purposes
    is_attendee = request.user in meeting.attendees.all()

    context = {
        'meeting': meeting,
        'page_title': meeting.title,
        'is_attendee': is_attendee,
        'current_attendees_count': meeting.attendees.count()
    }
    return render(request, 'meetings/meeting_detail.html', context)

# --- Additional Imports (place at the top of your file) ---
from django.http import Http404
import datetime



def privacy_policy_view(request):
    return render(request, 'privacy.html', {})

def terms_of_service_view(request):
    return render(request, 'terms.html', {})